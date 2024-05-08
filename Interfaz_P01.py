import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

class DatabaseApp:
    def __init__(self, master):
        # Inicialización de la aplicación de base de datos
        self.master = master
        self.master.title("Database App")
        
        # Conexión a la base de datos
        self.conn = sqlite3.connect('CRU_database.db')
        self.cursor = self.conn.cursor()

        # Inicializar selected_item como None
        self.selected_item = None
        
        # Crear los widgets de la interfaz gráfica
        self.create_widgets()

    def create_widgets(self):
        # Crear el tab control para gestionar las pestañas
        self.tabControl = ttk.Notebook(self.master)
        self.tabControl.pack(expand=1, fill="both")

        # Lista de tablas para mostrar en las pestañas
        tables = ["TopeFormaciones", "Metadata", "EditTopeFormaciones", "EditMetadata"]
        self.tab_frames = []

        # Iterar sobre las tablas para crear las pestañas y los árboles de datos
        for table_name in tables:
            tab_frame = ttk.Frame(self.tabControl)
            self.tabControl.add(tab_frame, text=table_name)

            self.create_table(tab_frame, table_name)
            self.tab_frames.append((table_name, tab_frame))

    def create_table(self, tab_frame, table_name):
        # Crear el marco para el árbol de datos
        tree_frame = tk.Frame(tab_frame)
        tree_frame.pack(side="top", fill="both", expand=True)

        # Obtener las columnas de la tabla
        columns = self.get_columns(table_name)
        self.treeview = ttk.Treeview(tree_frame, columns=columns, show="headings")
        for column in columns:
            self.treeview.heading(column, text=column)
        self.treeview.pack(side="left", fill="both", expand=True)

        # Añadir barra de desplazamiento vertical
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.treeview.yview)
        scrollbar.pack(side="right", fill="y")
        self.treeview.configure(yscrollcommand=scrollbar.set)

        # Enlazar el evento de clic en el árbol de datos
        self.treeview.bind("<ButtonRelease-1>", lambda event, table_name=table_name: self.on_click(event, table_name))

        # Agregar botones de inserción, eliminación o actualización según la tabla
        if not table_name.startswith("Edit"):
            insert_button = tk.Button(tab_frame, text="Agregar Registro", command=lambda: self.insert_record(table_name))
            insert_button.pack(pady=5)
            delete_button = tk.Button(tab_frame, text="Eliminar Registro", command=lambda: self.delete_record(table_name))
            delete_button.pack(pady=5)
        else:
            update_button = tk.Button(tab_frame, text="Actualizar Registro", command=lambda: self.update_record(table_name))
            update_button.pack(pady=5)

        # Cargar los datos en el árbol de datos
        self.load_data(self.treeview, table_name)

    def get_columns(self, table_name):
        # Obtener los nombres de las columnas de la tabla
        self.cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [col[1] for col in self.cursor.fetchall()]
        return columns

    def load_data(self, treeview, table_name):
        # Cargar los datos desde la tabla en el árbol de datos
        treeview.delete(*treeview.get_children())
        self.cursor.execute(f"SELECT * FROM {table_name}")
        rows = self.cursor.fetchall()
        for row in rows:
            treeview.insert("", "end", values=row)

    def on_click(self, event, table_name):
    # Manejar el evento de clic en el árbol de datos
        if self.treeview.selection():
            self.selected_item = self.treeview.selection()[0]  # Tomar solo el primer elemento seleccionado
        else:
            self.selected_item = None  # No hay elementos seleccionados
            messagebox.showwarning("Advertencia", "Por favor seleccione un registro en la tabla")



    def insert_record(self, table_name):
        # Función para insertar un registro en la tabla
        form = tk.Toplevel(self.master)
        form.title("Agregar Registro")

        labels = self.get_columns(table_name)[1:]
        entries = []

        for i, label in enumerate(labels):
            tk.Label(form, text=label).grid(row=i, column=0, padx=10, pady=5, sticky="e")
            entry = tk.Entry(form)
            entry.grid(row=i, column=1, padx=10, pady=5)
            entries.append(entry)

        insert_button = tk.Button(form, text="Insertar", command=lambda: self.insert_to_table(form, table_name, entries))
        insert_button.grid(row=len(labels), columnspan=2, pady=5)

    def insert_to_table(self, form, table_name, entries):
        # Función para insertar los datos en la tabla y actualizar la vista
        data = [entry.get() for entry in entries]
        try:
            self.cursor.execute(f"INSERT INTO {table_name} VALUES (NULL, {','.join(['?'] * len(data))})", data)
            self.conn.commit()
            messagebox.showinfo("Éxito", "Registro insertado correctamente")
            form.destroy()
            self.load_data(self.get_current_tree(), table_name)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo insertar el registro: {str(e)}")

    def delete_record(self, table_name):
        # Función para eliminar un registro de la tabla y actualizar la vista
        try:
            if self.selected_item:
                confirmation = messagebox.askyesno("Confirmar", "¿Estás seguro de que deseas eliminar este registro?")
                if confirmation:
                    id_column = "id_Formacion" if table_name.startswith("Tope") else "id_metadata"
                    self.cursor.execute(f"DELETE FROM {table_name} WHERE {id_column}=?", (self.selected_item,))
                    self.conn.commit()
                    messagebox.showinfo("Éxito", "Registro eliminado correctamente")
                    self.load_data(self.get_current_tree(), table_name)
            else:
                messagebox.showwarning("Advertencia", "Por favor seleccione un registro para eliminar")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar el registro: {str(e)}")


    def update_record(self, table_name):
        # Función para actualizar un registro de la tabla y actualizar la vista
        try:
            if self.selected_item:
                form = tk.Toplevel(self.master)
                form.title("Actualizar Registro")

                labels = self.get_columns(table_name)[1:]
                entries = []

                self.cursor.execute(f"SELECT * FROM {table_name} WHERE ID=?", (self.selected_item,))
                row = self.cursor.fetchone()

                for i, label in enumerate(labels):
                    tk.Label(form, text=label).grid(row=i, column=0, padx=10, pady=5, sticky="e")
                    entry = tk.Entry(form)
                    entry.grid(row=i, column=1, padx=10, pady=5)
                    entry.insert(0, row[i + 1])
                    entries.append(entry)

                update_button = tk.Button(form, text="Actualizar", command=lambda: self.update_to_table(form, table_name, entries, self.selected_item))
                update_button.grid(row=len(labels), columnspan=2, pady=5)
            else:
                messagebox.showwarning("Advertencia", "Por favor seleccione un registro para actualizar")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar el registro: {str(e)}")

    def update_to_table(self, form, table_name, entries, record_id):
        # Función para actualizar los datos en la tabla y actualizar la vista
        data = [entry.get() for entry in entries]
        try:
            set_clause = ','.join([f"{label} = ?" for label in self.get_columns(table_name)[1:]])
            self.cursor.execute(f"UPDATE {table_name} SET {set_clause} WHERE ID=?", data + [record_id])
            self.conn.commit()
            messagebox.showinfo("Éxito", "Registro actualizado correctamente")
            form.destroy()
            self.load_data(self.get_current_tree(), table_name)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar el registro: {str(e)}")

    def get_current_tree(self):
        # Obtener el árbol de datos de la pestaña actual
        selected_tab = self.tabControl.index(self.tabControl.select())
        if selected_tab == 0:
            return self.tab_frames[0][1].winfo_children()[0].winfo_children()[0]
        elif selected_tab == 1:
            return self.tab_frames[1][1].winfo_children()[0].winfo_children()[0]
        elif selected_tab == 2:
            return self.tab_frames[2][1].winfo_children()[0].winfo_children()[0]
        elif selected_tab == 3:
            return self.tab_frames[3][1].winfo_children()[0].winfo_children()[0]

def main():
    # Función principal para ejecutar la aplicación
    root = tk.Tk()
    app = DatabaseApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
