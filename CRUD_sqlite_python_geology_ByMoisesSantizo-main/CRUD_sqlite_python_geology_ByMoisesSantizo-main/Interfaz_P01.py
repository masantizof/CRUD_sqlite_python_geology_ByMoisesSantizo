import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import re  # Importar el módulo re

class DatabaseApp:
    def __init__(self, master):
        self.master = master
        self.master.title("App postulaciion Slg Moisés Santizo")
        self.conn = sqlite3.connect('CRU_database.db')
        self.cursor = self.conn.cursor()
        self.create_widgets()

    def create_widgets(self):
        self.tabControl = ttk.Notebook(self.master)
        self.tabControl.pack(expand=1, fill="both")
        tables = ["topeformaciones", "metadata", "edittopeformaciones", "editmetadata"]
        self.tab_frames = []
        self.treeviews = {}
        for table_name in tables:
            tab_frame = ttk.Frame(self.tabControl)
            self.tabControl.add(tab_frame, text=table_name)
            treeview = self.create_table(tab_frame, table_name)
            self.treeviews[table_name] = treeview
            self.tab_frames.append((table_name, tab_frame))

        # Botón de reinicio
        reset_button = tk.Button(self.master, text="Reiniciar", command=self.reset_app)
        reset_button.pack(pady=10)

    def create_table(self, tab_frame, table_name):
        tree_frame = tk.Frame(tab_frame)
        tree_frame.pack(side="top", fill="both", expand=True)

        columns = self.get_columns(table_name)
        treeview = ttk.Treeview(tree_frame, columns=columns, show="headings")
        for column in columns:
            treeview.heading(column, text=column)
        treeview.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=treeview.yview)
        scrollbar.pack(side="right", fill="y")
        treeview.configure(yscrollcommand=scrollbar.set)

        treeview.bind("<ButtonRelease-1>", lambda event, table_name=table_name: self.on_select(event, table_name))

        if not table_name.startswith("edit"):
            insert_button = tk.Button(tab_frame, text="Agregar Registro", command=lambda: self.insert_record(table_name, treeview))
            insert_button.pack(pady=5)
            delete_button = tk.Button(tab_frame, text="Eliminar Registro", command=lambda: self.delete_record(table_name, treeview))
            delete_button.pack(pady=5)
        else:
            update_button = tk.Button(tab_frame, text="Actualizar Registro", command=lambda: self.update_record(table_name, treeview))
            update_button.pack(pady=5)

        self.load_data(treeview, table_name)
        return treeview

    def get_columns(self, table_name):
        self.cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [col[1] for col in self.cursor.fetchall()]
        return columns

    def load_data(self, treeview, table_name):
        treeview.delete(*treeview.get_children())
        self.cursor.execute(f"SELECT * FROM {table_name}")
        rows = self.cursor.fetchall()
        for row in rows:
            treeview.insert("", "end", values=row, iid=row[0])

    def on_select(self, event, table_name):
        treeview = event.widget
        if treeview.selection():
            self.selected_item = treeview.selection()[0]
        else:
            self.selected_item = None

    def insert_record(self, table_name, treeview):
        form = tk.Toplevel(self.master)
        form.title("Agregar Registro")

        labels = self.get_columns(table_name)[1:]
        entries = []

        for i, label in enumerate(labels):
            tk.Label(form, text=label).grid(row=i, column=0, padx=10, pady=5, sticky="e")
            entry = tk.Entry(form)
            entry.grid(row=i, column=1, padx=10, pady=5)
            entries.append(entry)

            # Validar entrada según el tipo de dato
            if table_name == "topeformaciones" and label in ["base_md", "tope_md"]:
                entry.config(validate="key", validatecommand=(form.register(self.validate_number), "%P"))

        insert_button = tk.Button(form, text="Insertar", command=lambda: self.insert_to_table(form, table_name, entries, treeview))
        insert_button.grid(row=len(labels), columnspan=2, pady=5)

    def validate_number(self, input_str):
        return re.match(r'^[0-9]*$', input_str) is not None

    def insert_to_table(self, form, table_name, entries, treeview):
        data = [entry.get() for entry in entries]
        try:
            if table_name == "topeformaciones":
                base_md = int(data[1])
                tope_md = int(data[2])
                espesor_md = tope_md - base_md
                data[3] = str(espesor_md)

            self.cursor.execute(f"INSERT INTO {table_name} VALUES (NULL, {','.join(['?'] * len(data))})", data)
            self.conn.commit()
            self.load_data(treeview, table_name)
            messagebox.showinfo("Éxito", "Registro insertado correctamente")
            form.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo insertar el registro: {str(e)}")

    def delete_record(self, table_name, treeview):
        if self.selected_item:
            try:
                confirmation = messagebox.askyesno("Confirmar", "¿Estás seguro de que deseas eliminar este registro?")
                if confirmation:
                    id_column = "id_" + table_name.split("Edit")[-1].lower()
                    self.cursor.execute(f"DELETE FROM {table_name} WHERE {id_column}=?", (self.selected_item,))
                    self.conn.commit()
                    self.load_data(treeview, table_name)  # Actualizar el Treeview con los datos actualizados
                    messagebox.showinfo("Éxito", "Registro eliminado correctamente")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar el registro: {str(e)}")
        else:
            messagebox.showwarning("Advertencia", "Por favor seleccione un registro para eliminar")

    def update_record(self, table_name, treeview):
        if self.selected_item:
            try:
                form = tk.Toplevel(self.master)
                form.title("Actualizar Registro")

                labels = self.get_columns(table_name)[1:]
                entries = []

                id_column = "id_" + table_name.split("Edit")[-1].lower()
                self.cursor.execute(f"SELECT * FROM {table_name} WHERE {id_column}=?", (self.selected_item,))
                row = self.cursor.fetchone()

                for i, label in enumerate(labels):
                    tk.Label(form, text=label).grid(row=i, column=0, padx=10, pady=5, sticky="e")
                    entry = tk.Entry(form)
                    entry.grid(row=i, column=1, padx=10, pady=5)
                    entry.insert(0, row[i+1])
                    entries.append(entry)

                update_button = tk.Button(form, text="Actualizar", command=lambda: self.update_to_table(form, table_name, entries, self.selected_item, treeview))
                update_button.grid(row=len(labels), columnspan=2, pady=5)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo actualizar el registro: {str(e)}")
        else:
            messagebox.showwarning("Advertencia", "Por favor seleccione un registro para actualizar")

    def update_to_table(self, form, table_name, entries, selected_item, treeview):
        data = [entry.get() for entry in entries]
        try:
            id_column = "id_" + table_name.split("Edit")[-1].lower()
            self.cursor.execute(f"UPDATE {table_name} SET {' = ?, '.join(self.get_columns(table_name)[1:])} = ? WHERE {id_column} = ?", data + [selected_item])
            self.conn.commit()
            self.load_data(treeview, table_name)  # Actualizar el Treeview con los datos actualizados
            messagebox.showinfo("Éxito", "Registro actualizado correctamente")
            form.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar el registro: {str(e)}")

    def reset_app(self):
        # Reiniciar la aplicación
        self.master.destroy()
        root = tk.Tk()
        app = DatabaseApp(root)
        root.mainloop()

def main():
    root = tk.Tk()
    app = DatabaseApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
