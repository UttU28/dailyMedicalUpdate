import tkinter as tk
from tkinter import ttk, filedialog
import sv_ttk
from extract import extractClaimData
import json
import threading
import sys
import io
import os
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DND_AVAILABLE = True
except ImportError:
    DND_AVAILABLE = False
    TkinterDnD = tk.Tk

class TextRedirector:
    def __init__(self, textWidget):
        self.textWidget = textWidget
    
    def write(self, s):
        if s and s.strip():
            self.textWidget.insert(tk.END, s)
            self.textWidget.see(tk.END)
            self.textWidget.update_idletasks()
        return len(s) if s else 0
    
    def flush(self):
        pass
    
    def isatty(self):
        return False

class ClaimProcessorUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Medical Claim Processor")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        self.selectedFiles = []
        self.headlessMode = tk.BooleanVar(value=True)  # Default to headless
        self.originalStdout = sys.stdout
        self.originalStderr = sys.stderr
        
        sv_ttk.set_theme("dark")
        
        self.createWidgets()
        self.setupDragAndDrop()
        self.setupLogRedirect()
        
    def createWidgets(self):
        mainFrame = ttk.Frame(self.root, padding="15")
        mainFrame.pack(fill=tk.BOTH, expand=True)
        
        headerFrame = ttk.Frame(mainFrame)
        headerFrame.pack(fill=tk.X, pady=(0, 20))
        
        titleLabel = ttk.Label(headerFrame, text="Medical Claim Processor", font=("Segoe UI", 20, "bold"))
        titleLabel.pack()
        
        subtitleLabel = ttk.Label(headerFrame, text="Extract and process medical claim data", font=("Segoe UI", 10))
        subtitleLabel.pack(pady=(5, 0))
        
        fileSelectionFrame = ttk.LabelFrame(mainFrame, text="File Selection", padding="15")
        fileSelectionFrame.pack(fill=tk.X, pady=(0, 15))
        
        buttonFrame = ttk.Frame(fileSelectionFrame)
        buttonFrame.pack(fill=tk.X, pady=(0, 10))
        
        selectButton = ttk.Button(buttonFrame, text="📁 Select Files", command=self.selectFiles, width=20)
        selectButton.pack(side=tk.LEFT, padx=(0, 10))
        
        clearButton = ttk.Button(buttonFrame, text="🗑️ Clear All", command=self.clearFiles, width=15)
        clearButton.pack(side=tk.LEFT)
        
        if DND_AVAILABLE:
            dropLabel = ttk.Label(fileSelectionFrame, text="💡 Tip: Drag & drop .txt files here", font=("Segoe UI", 9), foreground="gray")
            dropLabel.pack(anchor=tk.W, pady=(5, 10))
        
        filesLabel = ttk.Label(fileSelectionFrame, text="Selected Files:", font=("Segoe UI", 11, "bold"))
        filesLabel.pack(anchor=tk.W, pady=(0, 8))
        
        filesFrame = ttk.Frame(fileSelectionFrame)
        filesFrame.pack(fill=tk.X)
        
        scrollbar = ttk.Scrollbar(filesFrame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.filesListbox = tk.Listbox(filesFrame, yscrollcommand=scrollbar.set, bg="#2b2b2b", fg="#e0e0e0", 
                                       selectbackground="#0078d4", selectforeground="white", 
                                       font=("Segoe UI", 10), relief=tk.FLAT, borderwidth=2,
                                       highlightthickness=1, highlightbackground="#404040", height=4)
        self.filesListbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.filesListbox.yview)
        
        actionFrame = ttk.Frame(mainFrame)
        actionFrame.pack(fill=tk.X, pady=(0, 15))
        
        # Headless mode checkbox
        optionsFrame = ttk.Frame(actionFrame)
        optionsFrame.pack(side=tk.LEFT, padx=(0, 15))
        
        headlessCheckbox = ttk.Checkbutton(
            optionsFrame, 
            text="Headless Mode", 
            variable=self.headlessMode,
            onvalue=True, 
            offvalue=False
        )
        headlessCheckbox.pack(side=tk.LEFT)
        
        # Help text for headless mode
        headlessHelp = ttk.Label(
            optionsFrame, 
            text="(Run browser in background)", 
            font=("Segoe UI", 8),
            foreground="gray"
        )
        headlessHelp.pack(side=tk.LEFT, padx=(5, 0))
        
        self.processButton = ttk.Button(actionFrame, text="🚀 Process Files", command=self.processFiles, state=tk.DISABLED, width=25)
        self.processButton.pack(side=tk.LEFT, padx=(0, 10))
        
        self.extractButton = ttk.Button(actionFrame, text="📊 Extract Data Only", command=self.extractDataOnly, state=tk.DISABLED, width=25)
        self.extractButton.pack(side=tk.LEFT)
        
        logFrame = ttk.LabelFrame(mainFrame, text="Activity Log", padding="12")
        logFrame.pack(fill=tk.BOTH, expand=True)
        
        logToolbar = ttk.Frame(logFrame)
        logToolbar.pack(fill=tk.X, pady=(0, 8))
        
        clearLogButton = ttk.Button(logToolbar, text="Clear Log", command=self.clearLog, width=12)
        clearLogButton.pack(side=tk.RIGHT)
        
        logScrollbar = ttk.Scrollbar(logFrame)
        logScrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.logText = tk.Text(logFrame, yscrollcommand=logScrollbar.set, bg="#1e1e1e", fg="#d4d4d4", 
                              wrap=tk.WORD, font=("Consolas", 9), relief=tk.FLAT, borderwidth=2,
                              highlightthickness=1, highlightbackground="#404040", padx=8, pady=8)
        self.logText.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        logScrollbar.config(command=self.logText.yview)
        
        self.log("✓ Application started. Ready to select files.")
    
    def setupDragAndDrop(self):
        if DND_AVAILABLE:
            self.filesListbox.drop_target_register(DND_FILES)
            self.filesListbox.dnd_bind('<<Drop>>', self.onDrop)
            self.log("✓ Drag & drop enabled. Drop files here!")
        else:
            self.log("ℹ Note: Install tkinterdnd2 for drag & drop support")
    
    def clearLog(self):
        self.logText.delete(1.0, tk.END)
        self.log("Log cleared.")
    
    def onDrop(self, event):
        files = self.root.tk.splitlist(event.data)
        added = 0
        skipped = 0
        
        for file in files:
            if file.endswith('.txt') and os.path.isfile(file):
                if file not in self.selectedFiles:
                    self.selectedFiles.append(file)
                    filename = os.path.basename(file)
                    self.filesListbox.insert(tk.END, filename)
                    self.log(f"✓ Dropped: {filename}")
                    added += 1
            else:
                filename = os.path.basename(file) if file else "unknown"
                self.log(f"⚠ Skipped: {filename} (not a .txt file)")
                skipped += 1
        
        if added > 0:
            self.log(f"✓ Added {added} file(s) via drag & drop")
        if skipped > 0:
            self.log(f"⚠ Skipped {skipped} file(s)")
        
        self.updateButtonStates()
    
    def setupLogRedirect(self):
        self.textRedirector = TextRedirector(self.logText)
    
    def startLogCapture(self):
        sys.stdout = self.textRedirector
        sys.stderr = self.textRedirector
    
    def stopLogCapture(self):
        sys.stdout = self.originalStdout
        sys.stderr = self.originalStderr
        
    def selectFiles(self):
        files = filedialog.askopenfilenames(
            title="Select Claim Text Files",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if files:
            for file in files:
                if file not in self.selectedFiles:
                    self.selectedFiles.append(file)
                    filename = os.path.basename(file)
                    self.filesListbox.insert(tk.END, filename)
                    self.log(f"✓ Added: {filename}")
            
            self.updateButtonStates()
            self.log(f"Total files selected: {len(self.selectedFiles)}")
    
    def clearFiles(self):
        count = len(self.selectedFiles)
        self.selectedFiles.clear()
        self.filesListbox.delete(0, tk.END)
        self.log(f"🗑️ Cleared {count} file(s).")
        self.updateButtonStates()
    
    def updateButtonStates(self):
        if len(self.selectedFiles) > 0:
            self.processButton.config(state=tk.NORMAL)
            self.extractButton.config(state=tk.NORMAL)
        else:
            self.processButton.config(state=tk.DISABLED)
            self.extractButton.config(state=tk.DISABLED)
    
    def log(self, message):
        self.logText.insert(tk.END, f"{message}\n")
        self.logText.see(tk.END)
        self.root.update_idletasks()
    
    def extractDataOnly(self):
        if not self.selectedFiles:
            self.log("No files selected.")
            return
        
        self.log("=" * 60)
        self.log("Starting data extraction...")
        
        def extractInThread():
            try:
                self.startLogCapture()
                
                for idx, file in enumerate(self.selectedFiles, 1):
                    print(f"\n[{idx}/{len(self.selectedFiles)}] Extracting from: {file}")
                    try:
                        jsonOutput = extractClaimData(file)
                        if jsonOutput:
                            data = json.loads(jsonOutput)
                            print(f"✓ Successfully extracted data")
                            print(f"  - Name: {data.get('name', 'N/A')}")
                            print(f"  - ID: {data.get('id', 'N/A')}")
                            print(f"  - Procedures: {len(data.get('procedures', []))}")
                            print(f"  - Signature Date: {data.get('signatureDate', 'N/A')}")
                        else:
                            print(f"✗ Failed to extract data from {file}")
                    except Exception as e:
                        print(f"✗ Error extracting {file}: {str(e)}")
                
                print(f"\n{'='*60}")
                print("Extraction complete!")
                
            except Exception as e:
                import traceback
                print(f"[ERROR] Error during extraction: {e}")
                traceback.print_exc()
            finally:
                self.stopLogCapture()
        
        thread = threading.Thread(target=extractInThread, daemon=True)
        thread.start()
    
    def processFiles(self):
        if not self.selectedFiles:
            self.log("No files selected.")
            return
        
        # Get headless mode setting from checkbox
        headlessMode = self.headlessMode.get()
        
        self.log("=" * 60)
        self.log("Starting file processing...")
        if headlessMode:
            self.log("Mode: HEADLESS (browser runs in background)")
        else:
            self.log("Mode: VISIBLE (browser window will be shown)")
        self.log("=" * 60)
        
        def processInThread():
            try:
                self.startLogCapture()
                from app import processSingleFile, createChromeSession, maximizeWindow
                
                # Use headless mode from checkbox
                driver = createChromeSession('uttu', headless=headlessMode)
                if not headlessMode:
                    maximizeWindow(driver)
                
                totalFiles = len(self.selectedFiles)
                successful = 0
                failed = 0
                
                for idx, file in enumerate(self.selectedFiles, 1):
                    if processSingleFile(driver, file):
                        successful += 1
                    else:
                        failed += 1
                
                print(f"\n{'='*60}")
                print(f"[INFO] Processing complete!")
                print(f"[INFO] Successful: {successful}/{totalFiles}")
                print(f"[INFO] Failed: {failed}/{totalFiles}")
                print(f"{'='*60}")
                
            except Exception as e:
                import traceback
                print(f"[ERROR] Error during processing: {e}")
                traceback.print_exc()
            finally:
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
