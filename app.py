import tkinter as tk
from tkinter import ttk, filedialog
import sv_ttk
from data_processor import (
    extractAndParseClaimData,
    formatDataForDisplay,
    processClaimDataForSteps,
    getDataSummary
)
from backend import processSingleFile, createChromeSession, maximizeWindow
import threading
import sys
import os
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DND_AVAILABLE = True
except ImportError:
    DND_AVAILABLE = False
    TkinterDnD = tk.Tk

class TextRedirector:
    """Redirects stdout/stderr to UI (filtered)"""
    def __init__(self, textWidget):
        self.textWidget = textWidget
        self.buffer = ""
    
    def write(self, s):
        if s:
            # Add to buffer for UI
            self.buffer += s
            
            # Process complete lines (ending with newline)
            while '\n' in self.buffer:
                line, self.buffer = self.buffer.split('\n', 1)
                if line.strip():
                    # Only show important lines in UI (filter verbose output)
                    if any(keyword in line for keyword in ['✓', '✗', '[INFO]', '[ERROR]', '[WARNING]', 'Starting', 'complete', 'Processing', 'Extracting']):
                        self.textWidget.insert(tk.END, line.strip() + '\n')
                        self.textWidget.see(tk.END)
                        self.textWidget.update_idletasks()
        
        return len(s) if s else 0
    
    def flush(self):
        if self.buffer.strip():
            self.buffer = ""
    
    def isatty(self):
        return False

class ClaimProcessorUI:
    def __init__(self, root):
        self.root = root
        self.root.title("I and My Doctors Clinic - Medical Claim Processor")
        self.root.geometry("700x500")
        self.root.minsize(600, 400)
        
        self.selectedFiles = []
        self.fileFrames = {}  # Store file frame widgets for removal
        self.headlessMode = tk.BooleanVar(value=True)  # Default to headless (checked)
        self.originalStdout = sys.stdout
        self.originalStderr = sys.stderr
        self.stopRequested = False  # Flag to signal stop
        self.currentDriver = None  # Store current driver for cleanup
        
        sv_ttk.set_theme("dark")
        
        self.createWidgets()
        self.setupDragAndDrop()
        self.setupLogRedirect()
    
        
    def createWidgets(self):
        # Main container
        self.mainContainer = ttk.Frame(self.root, padding="10")
        self.mainContainer.pack(fill=tk.BOTH, expand=True)
        
        # Step 1: File Selection View
        self.step1Frame = ttk.Frame(self.mainContainer)
        self.step1Frame.pack(fill=tk.BOTH, expand=True)
        
        # Step 2: Processing/Logs View
        self.step2Frame = ttk.Frame(self.mainContainer)
        
        self.createStep1View()
        self.createStep2View()
        
        # Show step 1 initially
        self.showStep1()
    
    def createStep1View(self):
        """Create the file selection view (Step 1)"""
        headerFrame = ttk.Frame(self.step1Frame)
        headerFrame.pack(fill=tk.X, pady=(0, 10))
        
        # Clinic branding
        clinicLabel = ttk.Label(headerFrame, text="I and My Doctors Clinic", font=("Segoe UI", 12), foreground="gray")
        clinicLabel.pack()
        
        titleLabel = ttk.Label(headerFrame, text="Medical Claim Processor", font=("Segoe UI", 16, "bold"))
        titleLabel.pack()
        
        fileSelectionFrame = ttk.LabelFrame(self.step1Frame, text="File Selection", padding="10")
        fileSelectionFrame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        buttonFrame = ttk.Frame(fileSelectionFrame)
        buttonFrame.pack(fill=tk.X, pady=(0, 8))
        
        selectButton = ttk.Button(buttonFrame, text="📁 Select Files", command=self.selectFiles, width=18)
        selectButton.pack(side=tk.LEFT, padx=(0, 8))
        
        clearButton = ttk.Button(buttonFrame, text="🗑️ Clear All", command=self.clearFiles, width=12)
        clearButton.pack(side=tk.LEFT)
        
        # Status label for drag & drop hint (smaller, less prominent)
        if DND_AVAILABLE:
            statusLabel = ttk.Label(buttonFrame, text="💡 Drag & drop .txt files", font=("Segoe UI", 8), foreground="gray")
            statusLabel.pack(side=tk.RIGHT)
        
        filesLabel = ttk.Label(fileSelectionFrame, text="Selected Files:", font=("Segoe UI", 10, "bold"))
        filesLabel.pack(anchor=tk.W, pady=(0, 5))
        
        # Create a canvas with scrollbar for the file list
        filesContainer = ttk.Frame(fileSelectionFrame)
        filesContainer.pack(fill=tk.BOTH, expand=True)
        
        self.filesCanvas = tk.Canvas(filesContainer, bg="#2b2b2b", highlightthickness=0)
        self.filesScrollbar = ttk.Scrollbar(filesContainer, orient="vertical", command=self.filesCanvas.yview)
        self.filesScrollFrame = ttk.Frame(self.filesCanvas)
        
        scrollable_window = self.filesCanvas.create_window((0, 0), window=self.filesScrollFrame, anchor="nw")
        
        def configure_scroll_region(event):
            # Update scroll region
            bbox = self.filesCanvas.bbox("all")
            if bbox:
                self.filesCanvas.configure(scrollregion=bbox)
                # Show/hide scrollbar based on content overflow
                canvas_height = self.filesCanvas.winfo_height()
                content_height = bbox[3] - bbox[1]
                if content_height > canvas_height:
                    self.filesScrollbar.pack(side=tk.RIGHT, fill=tk.Y)
                else:
                    self.filesScrollbar.pack_forget()
            else:
                self.filesCanvas.configure(scrollregion=(0, 0, 0, 0))
                self.filesScrollbar.pack_forget()
        
        def configure_canvas_width(event):
            canvas_width = event.width
            self.filesCanvas.itemconfig(scrollable_window, width=canvas_width)
            # Recheck scrollbar after width change
            configure_scroll_region(event)
        
        def on_mousewheel(event):
            # Only scroll if content overflows
            bbox = self.filesCanvas.bbox("all")
            if bbox:
                canvas_height = self.filesCanvas.winfo_height()
                content_height = bbox[3] - bbox[1]
                if content_height > canvas_height:
                    # Windows uses delta, Linux uses num
                    if hasattr(event, 'delta') and event.delta:
                        delta = int(-1 * (event.delta / 120))
                    elif hasattr(event, 'num'):
                        delta = -1 if event.num == 4 else 1
                    else:
                        return
                    self.filesCanvas.yview_scroll(delta, "units")
                    return "break"
        
        self.filesScrollFrame.bind("<Configure>", configure_scroll_region)
        self.filesCanvas.bind("<Configure>", configure_canvas_width)
        
        self.filesCanvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.filesCanvas.configure(yscrollcommand=self.filesScrollbar.set)
        
        # Bind mousewheel to canvas, scrollable frame, and container
        # This ensures scrolling works when mouse is over any part of the file list area
        self.filesCanvas.bind("<MouseWheel>", on_mousewheel)
        self.filesScrollFrame.bind("<MouseWheel>", on_mousewheel)
        filesContainer.bind("<MouseWheel>", on_mousewheel)
        
        # Linux/Unix support
        if sys.platform.startswith('linux'):
            self.filesCanvas.bind("<Button-4>", on_mousewheel)
            self.filesCanvas.bind("<Button-5>", on_mousewheel)
            self.filesScrollFrame.bind("<Button-4>", on_mousewheel)
            self.filesScrollFrame.bind("<Button-5>", on_mousewheel)
            filesContainer.bind("<Button-4>", on_mousewheel)
            filesContainer.bind("<Button-5>", on_mousewheel)
        
        actionFrame = ttk.Frame(self.step1Frame)
        actionFrame.pack(fill=tk.X)
        
        # Headless mode checkbox
        headlessCheckbox = ttk.Checkbutton(
            actionFrame, 
            text="Headless Mode", 
            variable=self.headlessMode,
            onvalue=True, 
            offvalue=False
        )
        headlessCheckbox.pack(side=tk.LEFT, padx=(0, 10))
        
        # Button container on the right
        buttonContainer = ttk.Frame(actionFrame)
        buttonContainer.pack(side=tk.RIGHT)
        
        # Process Files button with green text (packed first, so it's rightmost)
        self.processButton = ttk.Button(buttonContainer, text="🚀 Process Files", command=self.processFiles, state=tk.DISABLED, width=20)
        # Style the process button with green text
        style = ttk.Style()
        style.configure("Green.TButton", foreground="green")
        style.map("Green.TButton", 
                 foreground=[("active", "green"), ("!disabled", "green"), ("disabled", "gray")])
        self.processButton.configure(style="Green.TButton")
        self.processButton.pack(side=tk.RIGHT, padx=(0, 0))
        
        # Extract Data Only button (default style) - packed second, so it's to the left
        self.extractButton = ttk.Button(buttonContainer, text="📊 Extract Data Only", command=self.extractDataOnly, state=tk.DISABLED, width=20)
        self.extractButton.pack(side=tk.RIGHT, padx=(0, 12))
    
    def createStep2View(self):
        """Create the processing/logs view (Step 2)"""
        headerFrame = ttk.Frame(self.step2Frame)
        headerFrame.pack(fill=tk.X, pady=(0, 10))
        
        titleLabel = ttk.Label(headerFrame, text="Processing Files", font=("Segoe UI", 16, "bold"))
        titleLabel.pack(side=tk.LEFT)
        
        backButton = ttk.Button(headerFrame, text="← Back to Files", command=self.showStep1, width=15)
        backButton.pack(side=tk.RIGHT)
        
        # Progress section
        progressFrame = ttk.LabelFrame(self.step2Frame, text="Progress", padding="10")
        progressFrame.pack(fill=tk.X, pady=(0, 10))
        
        # File count label
        self.fileCountLabel = ttk.Label(progressFrame, text="", font=("Segoe UI", 9), foreground="gray")
        self.fileCountLabel.pack(anchor=tk.W, pady=(0, 5))
        
        self.progressLabel = ttk.Label(progressFrame, text="Ready to start...", font=("Segoe UI", 10))
        self.progressLabel.pack(anchor=tk.W, pady=(0, 5))
        
        self.progressBar = ttk.Progressbar(progressFrame, mode='determinate', length=400)
        self.progressBar.pack(fill=tk.X, pady=(0, 5))
        
        self.statusLabel = ttk.Label(progressFrame, text="", font=("Segoe UI", 9), foreground="gray")
        self.statusLabel.pack(anchor=tk.W)
        
        logFrame = ttk.LabelFrame(self.step2Frame, text="Activity Log", padding="8")
        logFrame.pack(fill=tk.BOTH, expand=True)
        
        logToolbar = ttk.Frame(logFrame)
        logToolbar.pack(fill=tk.X, pady=(0, 8), padx=(8, 0))
        
        buttonContainer = ttk.Frame(logToolbar)
        buttonContainer.pack(side=tk.RIGHT)
        
        # Stop button with red text (same style as Clear Log) - packed first, so it's rightmost
        self.stopButton = ttk.Button(buttonContainer, text="⏹ Stop", command=self.stopProcessing, 
                                     width=12, state=tk.DISABLED)
        # Style the stop button with red text
        style = ttk.Style()
        style.configure("Red.TButton", foreground="red")
        style.map("Red.TButton", 
                 foreground=[("active", "red"), ("!disabled", "red"), ("disabled", "gray")])
        self.stopButton.configure(style="Red.TButton")
        self.stopButton.pack(side=tk.RIGHT, padx=(0, 0))
        
        # Clear Log button - packed second, so it's to the left
        clearLogButton = ttk.Button(buttonContainer, text="Clear Log", command=self.clearLog, width=12)
        clearLogButton.pack(side=tk.RIGHT, padx=(0, 12))
        
        logScrollbar = ttk.Scrollbar(logFrame)
        logScrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.logText = tk.Text(logFrame, yscrollcommand=logScrollbar.set, bg="#1e1e1e", fg="#d4d4d4", 
                              wrap=tk.WORD, font=("Consolas", 9), relief=tk.FLAT, borderwidth=2,
                              highlightthickness=1, highlightbackground="#404040", padx=8, pady=8)
        self.logText.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        logScrollbar.config(command=self.logText.yview)
    
    def showStep1(self):
        """Show Step 1: File Selection"""
        self.step2Frame.pack_forget()
        self.step1Frame.pack(fill=tk.BOTH, expand=True)
    
    def showStep2(self):
        """Show Step 2: Processing/Logs"""
        self.step1Frame.pack_forget()
        self.step2Frame.pack(fill=tk.BOTH, expand=True)
        # Clear log and reset progress when switching to step 2
        if hasattr(self, 'logText') and self.logText:
            self.logText.delete(1.0, tk.END)
        if hasattr(self, 'progressBar') and self.progressBar:
            self.progressBar['value'] = 0
        if hasattr(self, 'progressLabel') and self.progressLabel:
            self.progressLabel.config(text="Ready to start...")
        if hasattr(self, 'statusLabel') and self.statusLabel:
            self.statusLabel.config(text="")
        if hasattr(self, 'fileCountLabel') and self.fileCountLabel:
            self.fileCountLabel.config(text="")
        # Reset stop button
        self.stopRequested = False
        if hasattr(self, 'stopButton') and self.stopButton:
            self.stopButton.config(state=tk.DISABLED)
    
    def stopProcessing(self):
        """Stop the current processing"""
        self.stopRequested = True
        if hasattr(self, 'stopButton') and self.stopButton:
            self.stopButton.config(state=tk.DISABLED)
        print("\n[STOP] Stop requested by user...")
        self.log("⏹ Stop requested. Finishing current step and stopping...")
        
        # Try to close driver if it exists
        if self.currentDriver:
            try:
                print("[STOP] Closing browser session...")
                self.currentDriver.quit()
                self.currentDriver = None
            except Exception as e:
                pass  # Silently ignore errors when stopping
    
    def setupDragAndDrop(self):
        if DND_AVAILABLE:
            # Register drag and drop on the canvas
            self.filesCanvas.drop_target_register(DND_FILES)
            self.filesCanvas.dnd_bind('<<Drop>>', self.onDrop)
        # Don't log here since logText might not exist yet
    
    def clearLog(self):
        self.logText.delete(1.0, tk.END)
        self.log("Log cleared.")
    
    def addFileToList(self, filepath):
        """Add a file to the list with a remove button"""
        if filepath in self.selectedFiles:
            return None  # Already added
        
        self.selectedFiles.append(filepath)
        filename = os.path.basename(filepath)
        
        # Create a frame for each file entry
        fileFrame = ttk.Frame(self.filesScrollFrame)
        fileFrame.pack(fill=tk.X, padx=2, pady=2)
        
        # File label
        fileLabel = ttk.Label(fileFrame, text=filename, font=("Segoe UI", 9))
        fileLabel.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))
        
        # Remove button
        removeBtn = ttk.Button(fileFrame, text="✕", command=lambda f=filepath: self.removeFile(f), width=3)
        removeBtn.pack(side=tk.RIGHT, padx=(0, 5))
        
        # Bind mousewheel to the file frame and its children for scrolling
        def on_file_mousewheel(event):
            # Forward the event to canvas
            bbox = self.filesCanvas.bbox("all")
            if bbox:
                canvas_height = self.filesCanvas.winfo_height()
                content_height = bbox[3] - bbox[1]
                if content_height > canvas_height:
                    if hasattr(event, 'delta') and event.delta:
                        delta = int(-1 * (event.delta / 120))
                    elif hasattr(event, 'num'):
                        delta = -1 if event.num == 4 else 1
                    else:
                        return
                    self.filesCanvas.yview_scroll(delta, "units")
                    return "break"
        
        fileFrame.bind("<MouseWheel>", on_file_mousewheel)
        fileLabel.bind("<MouseWheel>", on_file_mousewheel)
        removeBtn.bind("<MouseWheel>", on_file_mousewheel)
        
        if sys.platform.startswith('linux'):
            fileFrame.bind("<Button-4>", on_file_mousewheel)
            fileFrame.bind("<Button-5>", on_file_mousewheel)
            fileLabel.bind("<Button-4>", on_file_mousewheel)
            fileLabel.bind("<Button-5>", on_file_mousewheel)
            removeBtn.bind("<Button-4>", on_file_mousewheel)
            removeBtn.bind("<Button-5>", on_file_mousewheel)
        
        # Store the frame reference
        self.fileFrames[filepath] = fileFrame
        
        # Update canvas scroll region and scrollbar visibility
        self.filesCanvas.update_idletasks()
        bbox = self.filesCanvas.bbox("all")
        if bbox:
            self.filesCanvas.configure(scrollregion=bbox)
            # Show/hide scrollbar based on content overflow
            canvas_height = self.filesCanvas.winfo_height()
            content_height = bbox[3] - bbox[1]
            if content_height > canvas_height:
                self.filesScrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            else:
                self.filesScrollbar.pack_forget()
        else:
            self.filesCanvas.configure(scrollregion=(0, 0, 0, 0))
            self.filesScrollbar.pack_forget()
        
        self.updateButtonStates()
        return filename
    
    def log(self, message):
        """Log a message to the UI"""
        if hasattr(self, 'logText') and self.logText:
            self.logText.insert(tk.END, f"{message}\n")
            self.logText.see(tk.END)
            self.root.update_idletasks()
    
    def removeFile(self, filepath):
        """Remove a file from the list"""
        if filepath in self.selectedFiles:
            self.selectedFiles.remove(filepath)
            if filepath in self.fileFrames:
                self.fileFrames[filepath].destroy()
                del self.fileFrames[filepath]
            # Update canvas scroll region and scrollbar visibility
            self.filesCanvas.update_idletasks()
            bbox = self.filesCanvas.bbox("all")
            if bbox:
                self.filesCanvas.configure(scrollregion=bbox)
                # Show/hide scrollbar based on content overflow
                canvas_height = self.filesCanvas.winfo_height()
                content_height = bbox[3] - bbox[1]
                if content_height > canvas_height:
                    self.filesScrollbar.pack(side=tk.RIGHT, fill=tk.Y)
                else:
                    self.filesScrollbar.pack_forget()
            else:
                self.filesCanvas.configure(scrollregion=(0, 0, 0, 0))
                self.filesScrollbar.pack_forget()
            self.updateButtonStates()
    
    def onDrop(self, event):
        files = self.root.tk.splitlist(event.data)
        for file in files:
            if file.endswith('.txt') and os.path.isfile(file):
                self.addFileToList(file)
    
    def setupLogRedirect(self):
        # No setup needed - TextRedirector will be created when needed
        pass
    
    def startLogCapture(self):
        if hasattr(self, 'logText') and self.logText:
            self.textRedirector = TextRedirector(self.logText)
            sys.stdout = self.textRedirector
            sys.stderr = self.textRedirector
    
    def stopLogCapture(self):
        sys.stdout = self.originalStdout
        sys.stderr = self.originalStderr
    
    def updateFileProgress(self, step, totalSteps, status="", filename=""):
        """Update progress bar for current file processing (steps within a file)"""
        if hasattr(self, 'progressBar') and self.progressBar:
            progress = int((step / totalSteps) * 100) if totalSteps > 0 else 0
            self.progressBar['value'] = progress
            if filename:
                self.progressLabel.config(text=f"File: {os.path.basename(filename)} - Step {step}/{totalSteps} ({progress}%)")
            else:
                self.progressLabel.config(text=f"Step {step}/{totalSteps} ({progress}%)")
            if status:
                self.statusLabel.config(text=status)
            self.root.update_idletasks()
    
    def updateOverallProgress(self, currentFile, totalFiles):
        """Update overall file count (shown separately)"""
        if hasattr(self, 'fileCountLabel'):
            self.fileCountLabel.config(text=f"File {currentFile} of {totalFiles}")
        
    def selectFiles(self):
        files = filedialog.askopenfilenames(
            title="Select Claim Text Files",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if files:
            for file in files:
                self.addFileToList(file)
    
    def clearFiles(self):
        # Remove all file frames
        for filepath in list(self.selectedFiles):
            self.removeFile(filepath)
        self.updateButtonStates()
    
    def updateButtonStates(self):
        if len(self.selectedFiles) > 0:
            self.processButton.config(state=tk.NORMAL)
            self.extractButton.config(state=tk.NORMAL)
        else:
            self.processButton.config(state=tk.DISABLED)
            self.extractButton.config(state=tk.DISABLED)
    
    
    def extractDataOnly(self):
        if not self.selectedFiles:
            return
        
        # Switch to step 2 (logs view)
        self.showStep2()
        
        # Reset progress bar
        self.progressBar['value'] = 0
        totalFiles = len(self.selectedFiles)
        self.updateFileProgress(0, 1, "Starting data extraction...")
        self.updateOverallProgress(0, totalFiles)
        
        print("=" * 60)
        print("Starting data extraction...")
        print(f"Files to process: {totalFiles}")
        print("=" * 60)
        
        def extractInThread():
            try:
                self.startLogCapture()
                
                # Enable stop button
                if hasattr(self, 'stopButton') and self.stopButton:
                    self.stopButton.config(state=tk.NORMAL)
                
                successful = 0
                failed = 0
                
                for idx, file in enumerate(self.selectedFiles, 1):
                    # Check if stop was requested
                    if self.stopRequested:
                        print(f"[STOP] Extraction stopped at file {idx}/{totalFiles}")
                        break
                    
                    filename = os.path.basename(file)
                    self.updateOverallProgress(idx, totalFiles)
                    self.updateFileProgress(0, 1, f"Extracting: {filename}", filename)
                    
                    print(f"\n[{idx}/{totalFiles}] Extracting from: {filename}")
                    print("-" * 60)
                    
                    try:
                        data = extractAndParseClaimData(file)
                        if data:
                            print(f"✓ Successfully extracted data")
                            
                            # Show detailed data in UI
                            formatDataForDisplay(data)
                            
                            # Show summary in UI
                            summary = getDataSummary(data)
                            print(f"✓ Extracted: {summary}")
                            self.updateFileProgress(1, 1, f"✓ Extracted: {summary}", filename)
                            successful += 1
                        else:
                            print(f"✗ Failed to extract data from {filename}")
                            self.updateFileProgress(1, 1, f"✗ Failed", filename)
                            failed += 1
                    except Exception as e:
                        if not self.stopRequested:
                            print(f"✗ Error extracting {filename}: {str(e)}")
                            import traceback
                            traceback.print_exc()
                            self.updateFileProgress(1, 1, f"✗ Error", filename)
                            failed += 1
                    
                    # Reset progress bar for next file (if not stopped)
                    if not self.stopRequested:
                        self.progressBar['value'] = 0
                
                if self.stopRequested:
                    print(f"\n{'='*60}")
                    print(f"[STOP] Extraction STOPPED by user")
                    print(f"Completed: {successful}/{idx-1} files")
                    print(f"Successful: {successful}, Failed: {failed}")
                    print(f"{'='*60}")
                    self.updateFileProgress(1, 1, f"Stopped! Completed {successful} files")
                else:
                    print(f"\n{'='*60}")
                    print("Extraction complete!")
                    print(f"Successful: {successful}/{totalFiles}, Failed: {failed}/{totalFiles}")
                    self.updateFileProgress(1, 1, f"Complete! {successful} successful, {failed} failed")
                
            except Exception as e:
                if not self.stopRequested:
                    import traceback
                    print(f"[ERROR] Error during extraction: {e}")
                    traceback.print_exc()
            finally:
                # Disable stop button
                if hasattr(self, 'stopButton') and self.stopButton:
                    self.stopButton.config(state=tk.DISABLED)
                
                self.stopLogCapture()
        
        thread = threading.Thread(target=extractInThread, daemon=True)
        thread.start()
    
    def processFiles(self):
        if not self.selectedFiles:
            return
        
        # Switch to step 2 (logs view)
        self.showStep2()
        
        # Reset progress bar
        self.progressBar['value'] = 0
        totalFiles = len(self.selectedFiles)
        
        # Get headless mode setting from checkbox
        headlessMode = self.headlessMode.get()
        
        modeText = "HEADLESS" if headlessMode else "VISIBLE"
        self.updateFileProgress(0, 8, f"Initializing browser ({modeText} mode)...")
        self.updateOverallProgress(0, totalFiles)
        
        print("=" * 60)
        print("Starting file processing...")
        print(f"Files to process: {totalFiles}")
        print(f"Mode: {modeText} (browser runs in background)" if headlessMode else f"Mode: {modeText} (browser window will be shown)")
        print("=" * 60)
        
        def processInThread():
            driver = None
            try:
                self.startLogCapture()
                
                # Enable stop button
                if hasattr(self, 'stopButton') and self.stopButton:
                    self.stopButton.config(state=tk.NORMAL)
                
                # Use headless mode from checkbox
                print("[INFO] Creating Chrome session...")
                driver = createChromeSession('iandmydoc', headless=headlessMode)
                self.currentDriver = driver  # Store for stop functionality
                if not headlessMode:
                    maximizeWindow(driver)
                print("[INFO] Chrome session created successfully")
                
                # Check if stop was requested
                if self.stopRequested:
                    print("[STOP] Processing stopped before starting")
                    return
                
                successful = 0
                failed = 0
                
                # Define steps for progress tracking
                processing_steps = [
                    "Extracting data",
                    "Converting data format",
                    "Step 1: Finding member",
                    "Step 2: General info",
                    "Step 3: Diagnosis codes",
                    "Step 4: Service lines",
                    "Step 5: Provider details",
                    "Step 6: Attachments"
                ]
                
                for idx, file in enumerate(self.selectedFiles, 1):
                    # Check if stop was requested
                    if self.stopRequested:
                        print(f"[STOP] Processing stopped at file {idx}/{totalFiles}")
                        break
                    
                    filename = os.path.basename(file)
                    self.updateOverallProgress(idx, totalFiles)
                    self.updateFileProgress(0, 8, "", filename)
                    
                    print(f"\n[{idx}/{totalFiles}] Processing: {filename}")
                    
                    try:
                        # Step 0: Extract data
                        if self.stopRequested:
                            break
                        self.updateFileProgress(1, 8, processing_steps[0], filename)
                        print(f"[INFO] Extracting data from {filename}")
                        extractedData = extractAndParseClaimData(file)
                        if not extractedData:
                            raise ValueError(f"Failed to extract data from {filename}")
                        print(f"[INFO] Successfully extracted data")
                        
                        # Step 1: Convert data
                        if self.stopRequested:
                            break
                        self.updateFileProgress(2, 8, processing_steps[1], filename)
                        stepData = processClaimDataForSteps(extractedData)
                        if not stepData:
                            raise ValueError(f"Failed to convert data to step format")
                        step1Data, step2Data, step3Data, step4Data = stepData
                        print(f"[INFO] Data converted to step format")
                        
                        # Step 2: Execute Step 1 (Find member)
                        if self.stopRequested:
                            break
                        self.updateFileProgress(3, 8, processing_steps[2], filename)
                        print(f"[INFO] Executing Step 1: Finding member")
                        from pages.step1 import executeStep1
                        executeStep1(driver, step1Data['insuredId'], step1Data['insuredDob'])
                        
                        # Step 3: Execute Step 2 (General Info)
                        if self.stopRequested:
                            break
                        self.updateFileProgress(4, 8, processing_steps[3], filename)
                        print(f"[INFO] Executing Step 2: General info")
                        from pages.step2 import executeStep2
                        executeStep2(driver, step2Data['patientAccountNumber'], step2Data['providerSignatureDate'], step2Data['cliaNumber'])
                        
                        # Step 4: Execute Step 3 (Diagnosis Codes)
                        if self.stopRequested:
                            break
                        self.updateFileProgress(5, 8, processing_steps[4], filename)
                        print(f"[INFO] Executing Step 3: Diagnosis codes")
                        from pages.step3 import executeStep3
                        executeStep3(driver, step3Data['diagnosisCodes'])
                        
                        # Step 5: Execute Step 4 (Service Lines)
                        if self.stopRequested:
                            break
                        self.updateFileProgress(6, 8, processing_steps[5], filename)
                        print(f"[INFO] Executing Step 4: Service lines")
                        from pages.step4 import executeStep4
                        executeStep4(driver, step4Data['serviceLines'])
                        
                        # Step 6: Execute Step 5 (Provider Details)
                        if self.stopRequested:
                            break
                        self.updateFileProgress(7, 8, processing_steps[6], filename)
                        print(f"[INFO] Executing Step 5: Provider details")
                        from pages.step5 import executeStep5
                        executeStep5(driver)
                        
                        # Step 7: Execute Step 6 (Attachments)
                        if self.stopRequested:
                            break
                        self.updateFileProgress(8, 8, processing_steps[7], filename)
                        print(f"[INFO] Executing Step 6: Attachments")
                        from pages.step6 import executeStep6
                        executeStep6(driver)
                        
                        print(f"✓ Successfully processed: {filename}")
                        successful += 1
                        
                    except Exception as e:
                        if not self.stopRequested:
                            print(f"✗ Failed to process {filename}: {str(e)}")
                            import traceback
                            traceback.print_exc()
                            failed += 1
                    
                    # Reset progress bar for next file (if not stopped)
                    if not self.stopRequested:
                        self.progressBar['value'] = 0
                
                if self.stopRequested:
                    print(f"\n{'='*60}")
                    print(f"[STOP] Processing STOPPED by user")
                    print(f"Completed: {successful}/{idx-1} files")
                    print(f"Successful: {successful}, Failed: {failed}")
                    print(f"{'='*60}")
                    self.updateFileProgress(8, 8, f"Stopped! Completed {successful} files")
                else:
                    print(f"\n{'='*60}")
                    print(f"Processing complete!")
                    print(f"Successful: {successful}/{totalFiles}")
                    print(f"Failed: {failed}/{totalFiles}")
                    print(f"{'='*60}")
                    self.updateFileProgress(8, 8, f"Complete! {successful} successful, {failed} failed")
                
            except Exception as e:
                if not self.stopRequested:
                    import traceback
                    print(f"[ERROR] Error during processing: {e}")
                    traceback.print_exc()
                    self.updateFileProgress(8, 8, f"Error: {str(e)}")
            finally:
                # Cleanup
                if driver:
                    try:
                        if not self.stopRequested:
                            print("[INFO] Closing browser session...")
                        driver.quit()
                    except Exception as e:
                        pass  # Silently ignore errors when stopping
                    finally:
                        self.currentDriver = None
                
                # Disable stop button
                if hasattr(self, 'stopButton') and self.stopButton:
                    self.stopButton.config(state=tk.DISABLED)
                
                self.stopLogCapture()
        
        thread = threading.Thread(target=processInThread, daemon=True)
        thread.start()

def main():
    if DND_AVAILABLE:
        root = TkinterDnD.Tk()
    else:
        root = tk.Tk()
    app = ClaimProcessorUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
