import tkinter as tk
from tkinter import ttk, filedialog
import chardet

class FileBrowser:
    def __init__(self, root):
        self.root = root
        self.folder_structure = {}
        self.current_path = []

        # 使用 ttk 控件改进视觉效果
        self.listbox = tk.Listbox(root, width=60, height=20)
        self.scrollbar = ttk.Scrollbar(root, orient='vertical', command=self.listbox.yview)
        self.listbox.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side='right', fill='y')
        self.listbox.pack(side='left', fill='both', expand=True)

        self.load_button = ttk.Button(root, text="Load File", command=self.load_file)
        self.load_button.pack(side='top')

        self.back_button = ttk.Button(root, text='返回上级', command=self.go_back)
        self.back_button.pack(side='bottom')

        self.listbox.bind('<Double-1>', self.enter_folder)

    def load_file(self):
        filepath = filedialog.askopenfilename(
            title="Select file", 
            filetypes=(("Text files", "*.txt"), ("all files", "*.*"))
        )
        if filepath:
            self.process_file(filepath)

    def process_file(self, filepath):
        lines = self.read_file(filepath)
        if lines:
            frame = self.calculate_depths(lines)
            self.folder_structure = self.build_nested_dict(frame)
            self.update_listbox()

    def read_file(self, filepath):
        try:
            with open(filepath, 'rb') as file:
                raw_data = file.read(4096)  
                result = chardet.detect(raw_data)
                encoding = result['encoding']
            with open(filepath, 'r', encoding=encoding) as file:
                lines = file.readlines()
        except Exception as e:
            print(f"读取文件时出错：{e}")
            return []
        lines = [line.replace('\xa0', ' ') for line in lines]
        return lines[1:-2]

    def calculate_depths(self, lines):
        frame = []
        for line in lines:
            depth = 0
            while depth < len(line) and line[depth] in ' │├─└':
                depth += 1
            text = line[depth:-1].strip()
            frame.append((text, depth // 4 - 1))
        return frame

    def build_nested_dict(self, frame):
        root_dict = {}
        paths = {0: root_dict}
        for name, depth in frame:
            parent = paths[depth - 1] if depth > 0 else root_dict
            parent[name] = {}
            paths[depth] = parent[name]
        return root_dict

    def update_listbox(self):
        self.listbox.delete(0, tk.END)
        current_folder = self.get_current_folder()
        for item in current_folder:
            if current_folder[item]:
                self.listbox.insert(tk.END, item)
                self.listbox.itemconfig(tk.END, foreground='blue')
            else:
                self.listbox.insert(tk.END, item)
                self.listbox.itemconfig(tk.END, foreground='black')

    def get_current_folder(self):
        folder = self.folder_structure
        for key in self.current_path:
            folder = folder[key]
        return folder

    def go_back(self):
        if self.current_path:
            self.current_path.pop()
            self.update_listbox()

    def enter_folder(self, event):
        index = self.listbox.curselection()
        if index:
            item = self.listbox.get(index)
            current_folder = self.get_current_folder()
            if item in current_folder and current_folder[item]:
                self.current_path.append(item)
                self.update_listbox()

# 创建主窗口
root = tk.Tk()
root.title('文件浏览器')
app = FileBrowser(root)
root.mainloop()
