import tkinter as tk
from tkinter import filedialog, messagebox
from readingDocks import list_docx_files_in_folder, extractDataFrom
from writingDocks import callFromMaster
import os

class DocxProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("JC ChartWatcher")
        self.root.configure(bg="#2E2E2E")  # Dark background
        
        # Styling variables
        self.text_color = "#FFFFFF"
        self.bg_color = "#2E2E2E"
        self.entry_bg_color = "#3C3F41"
        self.button_bg_color = "#4A90E2"
        self.button_fg_color = "#FFFFFF"
        
        # Labels and Inputs for directories
        self.label_input_dir = tk.Label(root, text="Welcome to ChartWatcher", fg=self.text_color, bg=self.bg_color, font=("Arial", 15))
        self.label_input_dir.pack(pady=5)

        # Instruction text with wrapping
        instruction_text = """All DOCX files must follow a consistent naming convention: they should include the same month name and have a space-separated date (e.g., "Oct 28.docx"). Ensure there are no double spaces between the month and date, and the format for the month must be uniform across all files—using "Oct" in one file and "October" in another will not be acceptable. Additionally, the input directory should contain data for only one month at a time."""
        self.label_instructions = tk.Label(root, text=instruction_text, fg=self.text_color, bg=self.bg_color, font=("Arial", 8), wraplength=500, justify="left")
        self.label_instructions.pack(pady=5)
        
        self.label_input_dir = tk.Label(root, text="Folder that has DOCX files", fg=self.text_color, bg=self.bg_color, font=("Arial", 12))
        self.label_input_dir.pack(pady=2)
        
        self.input_dir = tk.Entry(root, width=50, bg=self.entry_bg_color, fg=self.text_color, insertbackground=self.text_color)
        self.input_dir.pack(pady=5, ipady=5)
        
        self.browse_input_button = tk.Button(root, text="Browse", command=self.browse_input_directory, bg=self.button_bg_color, fg=self.button_fg_color, activebackground="#357ABD", font=("Arial", 10, "bold"))
        self.browse_input_button.pack(pady=5, ipadx=10, ipady=5)
        
        self.label_output_dir = tk.Label(root, text="Folder to Store Output", fg=self.text_color, bg=self.bg_color, font=("Arial", 12))
        self.label_output_dir.pack(pady=2)
        
        self.output_dir = tk.Entry(root, width=50, bg=self.entry_bg_color, fg=self.text_color, insertbackground=self.text_color)
        self.output_dir.pack(pady=5, ipady=5)
        
        self.browse_output_button = tk.Button(root, text="Browse", command=self.browse_output_directory, bg=self.button_bg_color, fg=self.button_fg_color, activebackground="#357ABD", font=("Arial", 10, "bold"))
        self.browse_output_button.pack(pady=5, ipadx=10, ipady=5)
        
        # Process Button
        self.process_button = tk.Button(root, text="Process Files", command=self.process_files, bg=self.button_bg_color, fg=self.button_fg_color, activebackground="#357ABD", font=("Arial", 12, "bold"))
        self.process_button.pack(pady=20, ipadx=20, ipady=10)
        
        # Log or Status display
        self.log_text = tk.Text(root, height=5, width=60, state='disabled', bg=self.entry_bg_color, fg=self.text_color)
        self.log_text.pack(pady=5)
    
    def browse_input_directory(self):
        input_dir = filedialog.askdirectory()
        if input_dir:
            self.input_dir.delete(0, tk.END)
            self.input_dir.insert(0, input_dir)
    
    def browse_output_directory(self):
        output_dir = filedialog.askdirectory()
        if output_dir:
            self.output_dir.delete(0, tk.END)
            self.output_dir.insert(0, output_dir)
    
    def log_message(self, message):
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.config(state='disabled')
        self.log_text.yview(tk.END)  # Scroll to the end
    
    def process_files(self):
        input_dir = self.input_dir.get().strip()
        output_dir = self.output_dir.get().strip()
        
        # Check if directories are valid
        if not os.path.isdir(input_dir):
            messagebox.showerror("Error", "Invalid input directory")
            return
        
        if not os.path.isdir(output_dir):
            messagebox.showerror("Error", "Invalid output directory")
            return
        
        self.log_message(f"Processing files in {input_dir}")
        
        try:
            all_doc_files = list_docx_files_in_folder(input_dir)
            self.log_message(f"Found {len(all_doc_files)} DOCX files.")
            
            for file_name in all_doc_files:
                try:
                    self.log_message(f"Processing {file_name}...")
                    extractDataFrom(input_dir, file_name.replace('.docx', ''))
                    self.log_message(f"Successfully processed {file_name}")
                except Exception as e:
                    self.log_message(f"Error processing {file_name}: {str(e)}")
            
            self.log_message("Generating output documents...")
            callFromMaster(output_dir)
            self.log_message("Process complete!")
            
            messagebox.showinfo("Success", "All files have been processed successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = DocxProcessorApp(root)
    root.mainloop()
