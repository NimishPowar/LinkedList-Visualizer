import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLineEdit, QLabel, QTextEdit, QGridLayout, QGroupBox,
                             QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsObject)
from PyQt5.QtCore import Qt, QPropertyAnimation, pyqtProperty, QPointF, QRectF, QParallelAnimationGroup
from PyQt5.QtGui import QFont, QIcon, QColor, QPainter, QPen, QBrush

class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

class LinkedList:
    def __init__(self):
        self.head = None

    def append(self, data):
        new_node = Node(data)
        if self.head is None:
            self.head = new_node
            return
        
        temp = self.head
        while temp.next:
            temp = temp.next
        temp.next = new_node

    def prepend(self, data):
        new_node = Node(data)
        new_node.next = self.head
        self.head = new_node

    def delete_node(self, key):
        temp = self.head
        prev = None

        # Case 1: Node to delete is the head
        if temp and temp.data == key:
            self.head = temp.next
            temp = None
            return

        # Case 2: Node is in the middle or end
        while temp and temp.data != key:
            prev = temp
            temp = temp.next

        # Case 3: Node not found
        if temp is None:
            print(f"Node with data {key} not found.")
            return

        # Unlink the node
        prev.next = temp.next
        temp = None


    def count(self):
        if self.head is None:
            # print("LinkedList is empty")
            return 0
        
        count = 0
        temp = self.head
        while temp:
            count += 1
            temp = temp.next
        return count
        # print(f"The number of nodes are {count} in this SinglyLinkedList")

    def search(self, key):
        """Search for a node with given data, returns True if found"""
        temp = self.head
        while temp:
            if temp.data == key:
                return True
            temp = temp.next
        return False
    
    def insertion(self, data, key):
        temp = self.head
        new_node = Node(data)
        while temp:
            if temp.data == key:
                new_node.next = temp.next
                temp.next = new_node
                return
            temp = temp.next
        # print(f"Node with data {key} not found.")
        # If not found, we might want to raise an error or handle it, 
        # but the GUI handles the pre-check or post-check usually.

    def reverse(self):
        """Reverse the linked list"""
        prev = None
        temp = self.head
        while temp:
            next_node = temp.next
            temp.next = prev
            prev = temp
            temp = next_node
        self.head = prev
        
    def __str__(self):
        elements = []
        temp = self.head
        while temp:
            elements.append(temp.data)
            temp = temp.next
        return " -> ".join(map(str, elements))


# --- Visual Animation Classes ---

class VisualNode(QGraphicsObject):
    def __init__(self, data, x, y):
        super().__init__()
        self.data = data
        self.setPos(x, y)
        self.radius = 25
        self.color = QColor('#4CAF50')
        self.text_color = Qt.white
        self._opacity = 1.0
        self.arrows = [] # Track connected arrows
        
        # Enable sending itemChange notifications
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)

    def add_arrow(self, arrow):
        if arrow not in self.arrows:
            self.arrows.append(arrow)

    def remove_arrow(self, arrow):
        if arrow in self.arrows:
            self.arrows.remove(arrow)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            for arrow in self.arrows:
                arrow.update_arrow()
        return super().itemChange(change, value)

    def boundingRect(self):
        return QRectF(-self.radius, -self.radius, 2 * self.radius, 2 * self.radius)

    def paint(self, painter, option, widget):
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setOpacity(self._opacity)
        
        # Draw node circle
        path = QRectF(-self.radius, -self.radius, 2 * self.radius, 2 * self.radius)
        painter.setBrush(QBrush(self.color))
        painter.setPen(QPen(Qt.black, 2))
        painter.drawEllipse(path)
        
        # Draw text
        painter.setPen(self.text_color)
        painter.setFont(QFont('Arial', 12, QFont.Bold))
        painter.drawText(path, Qt.AlignCenter, str(self.data))

    @pyqtProperty(float)
    def opacity(self):
        return self._opacity

    @opacity.setter
    def opacity(self, val):
        self._opacity = val
        self.update()


class ArrowItem(QGraphicsItem):
    def __init__(self, start_item, end_item):
        super().__init__()
        self.start_item = start_item
        self.end_item = end_item
        self.setZValue(-1) # Draw behind nodes
        
    def update_arrow(self):
        self.prepareGeometryChange()
        self.update()

    def boundingRect(self):
        # A generous bounding rect to ensure updates happen
        return self.start_item.sceneBoundingRect().united(self.end_item.sceneBoundingRect())

    def paint(self, painter, option, widget):
        if not self.start_item.scene() or not self.end_item.scene():
            return

        start_pos = self.start_item.pos()
        end_pos = self.end_item.pos()
        
        # Calculate direction vector
        line = end_pos - start_pos
        length = (line.x()**2 + line.y()**2)**0.5
        
        if length == 0:
            return

        # Normalize
        dx = line.x() / length
        dy = line.y() / length
        
        # Radius of node (approx)
        r = 25 
        
        # Adjust start and end points to be on the edge of the circle
        start_edge = start_pos + QPointF(dx * r, dy * r)
        end_edge = end_pos - QPointF(dx * r, dy * r)
        
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(Qt.black, 2))
        painter.drawLine(start_edge, end_edge)
        
        # Draw arrow head
        arrow_size = 10
        angle = 3.14159 / 6 # 30 degrees
        
        # Rotate vector for arrow head
        # We need to rotate (dx, dy) by angle+pi (pointing back from end)
        
        # Back vector
        back_x = -dx
        back_y = -dy
        
        p1 = end_edge + QPointF(
            back_x * 0.866 - back_y * 0.5, # cos(30), sin(30)
            back_x * 0.5 + back_y * 0.866
        ) * arrow_size
        
        p2 = end_edge + QPointF(
            back_x * 0.866 + back_y * 0.5,
            -back_x * 0.5 + back_y * 0.866
        ) * arrow_size
        
        painter.setBrush(Qt.black)
        painter.drawPolygon(QPointF(end_edge), p1, p2)


class LinkedListCanvas(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.visual_nodes = [] # List of VisualNode objects
        self.arrows = []
        
        # Coordinate settings
        self.start_x = 50
        self.start_y = 100
        self.node_spacing = 100
        
        self.scene.setSceneRect(0, 0, 800, 300)

    def create_arrow(self, start, end):
        arrow = ArrowItem(start, end)
        start.add_arrow(arrow)
        end.add_arrow(arrow)
        self.scene.addItem(arrow)
        self.arrows.append(arrow)
        return arrow

    def clear_scene(self):
        self.scene.clear()
        self.visual_nodes = []
        self.arrows = []

    def sync_from_list(self, linked_list):
        """Ideally we animate nicely, but for bulk updates (reverse), logic sync is good."""
        self.clear_scene()
        temp = linked_list.head
        idx = 0
        prev_vnode = None
        
        while temp:
            vnode = VisualNode(temp.data, self.start_x + idx * self.node_spacing, self.start_y)
            self.scene.addItem(vnode)
            self.visual_nodes.append(vnode)
            
            if prev_vnode:
                self.create_arrow(prev_vnode, vnode)
            
            prev_vnode = vnode
            temp = temp.next
            idx += 1

    def animate_append(self, data):
        # Create new node at a spawn position (faded out) then move to place
        target_idx = len(self.visual_nodes)
        target_x = self.start_x + target_idx * self.node_spacing
        target_y = self.start_y
        
        # Spawn slightly above
        new_node = VisualNode(data, target_x, target_y - 50)
        new_node.opacity = 0.0
        self.scene.addItem(new_node)
        self.visual_nodes.append(new_node)
        
        # Add arrow if there's a predecessor
        if len(self.visual_nodes) > 1:
            prev_node = self.visual_nodes[-2]
            self.create_arrow(prev_node, new_node)
            
        # Animation
        anim_pos = QPropertyAnimation(new_node, b"pos")
        anim_pos.setDuration(500)
        anim_pos.setStartValue(QPointF(target_x, target_y - 50))
        anim_pos.setEndValue(QPointF(target_x, target_y))
        
        anim_op = QPropertyAnimation(new_node, b"opacity")
        anim_op.setDuration(500)
        anim_op.setStartValue(0.0)
        anim_op.setEndValue(1.0)
        
        self.group = QParallelAnimationGroup()
        self.group.addAnimation(anim_pos)
        self.group.addAnimation(anim_op)
        self.group.start()

    def animate_prepend(self, data):
        # Shift all existing nodes right
        self.group = QParallelAnimationGroup()
        
        for vnode in self.visual_nodes:
            anim = QPropertyAnimation(vnode, b"pos")
            anim.setDuration(500)
            anim.setStartValue(vnode.pos())
            anim.setEndValue(vnode.pos() + QPointF(self.node_spacing, 0))
            self.group.addAnimation(anim)
            
        # Create new node
        new_node = VisualNode(data, self.start_x, self.start_y - 50)
        new_node.opacity = 0.0
        self.scene.addItem(new_node)
        self.visual_nodes.insert(0, new_node)
        
        anim_new_pos = QPropertyAnimation(new_node, b"pos")
        anim_new_pos.setDuration(500)
        anim_new_pos.setStartValue(QPointF(self.start_x, self.start_y - 50))
        anim_new_pos.setEndValue(QPointF(self.start_x, self.start_y))
        
        anim_new_op = QPropertyAnimation(new_node, b"opacity")
        anim_new_op.setDuration(500)
        anim_new_op.setStartValue(0.0)
        anim_new_op.setEndValue(1.0)
        
        self.group.addAnimation(anim_new_pos)
        self.group.addAnimation(anim_new_op)
        
        # New arrow: new_node -> old_head
        if len(self.visual_nodes) > 1:
            arrow = self.create_arrow(self.visual_nodes[0], self.visual_nodes[1])
            self.arrows.insert(0, arrow)

        self.group.start()

    def animate_delete(self, index):
        if index < 0 or index >= len(self.visual_nodes):
            return
            
        target_node = self.visual_nodes[index]
        
        self.group = QParallelAnimationGroup()
        
        # Fade out target
        anim_op = QPropertyAnimation(target_node, b"opacity")
        anim_op.setDuration(500)
        anim_op.setStartValue(1.0)
        anim_op.setEndValue(0.0)
        self.group.addAnimation(anim_op)
        
        # Shift subsequent nodes left
        for i in range(index + 1, len(self.visual_nodes)):
            vnode = self.visual_nodes[i]
            anim = QPropertyAnimation(vnode, b"pos")
            anim.setDuration(500)
            anim.setStartValue(vnode.pos())
            anim.setEndValue(vnode.pos() - QPointF(self.node_spacing, 0))
            self.group.addAnimation(anim)
            
        def on_finished():
            # Remove target arrow connections?
            # When we rebuild or specific removal, we need to be careful.
            
            self.scene.removeItem(target_node)
            del self.visual_nodes[index]
            
            # Rebuild arrows to be safe/clean
            for arrow in self.arrows:
                self.scene.removeItem(arrow)
            self.arrows = []
            
            for i in range(len(self.visual_nodes) - 1):
                self.create_arrow(self.visual_nodes[i], self.visual_nodes[i+1])
                
        self.group.finished.connect(on_finished)
        self.group.start()

# --- Main GUI ---

class LinkedListGUI(QMainWindow):
    def __init__(self, linked_list):
        super().__init__()
        self.mylist = linked_list
        self.initUI()
        self.apply_styles()
        # Initialize canvas with current list state (empty)
        self.canvas.sync_from_list(self.mylist)
    
    def initUI(self):
        self.setWindowTitle('Linked List Visualizer')
        self.setGeometry(50, 50, 1000, 900)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("Linked List Visualizer")
        title.setFont(QFont('Arial', 22, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        # Animation Canvas
        self.canvas = LinkedListCanvas()
        self.canvas.setMinimumHeight(300)
        self.canvas.setStyleSheet("border: 2px solid #cccccc; border-radius: 5px; background-color: #f9f9f9;")
        main_layout.addWidget(self.canvas)

        # Input Group
        input_group = QGroupBox("Input Section")
        input_layout = QVBoxLayout()
        
        # Data input
        data_h_layout = QHBoxLayout()
        data_label = QLabel("Data:")
        data_label.setFont(QFont('Arial', 11, QFont.Bold))
        data_label.setMinimumWidth(80)
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Enter a number...")
        self.input_field.setMinimumHeight(35)
        self.input_field.setFont(QFont('Arial', 11))
        data_h_layout.addWidget(data_label)
        data_h_layout.addWidget(self.input_field)
        input_layout.addLayout(data_h_layout)
        
        # Key input
        key_h_layout = QHBoxLayout()
        key_label = QLabel("Key:")
        key_label.setFont(QFont('Arial', 11, QFont.Bold))
        key_label.setMinimumWidth(80)
        self.key_field = QLineEdit()
        self.key_field.setPlaceholderText("After which node (for insert)...")
        self.key_field.setMinimumHeight(35)
        self.key_field.setFont(QFont('Arial', 11))
        key_h_layout.addWidget(key_label)
        key_h_layout.addWidget(self.key_field)
        input_layout.addLayout(key_h_layout)
        
        input_group.setLayout(input_layout)
        main_layout.addWidget(input_group)
        
        # Buttons Group
        buttons_group = QGroupBox("Operations")
        buttons_layout = QGridLayout()
        buttons_layout.setSpacing(8)
        
        buttons_data = [
            ('Append', self.append_node, 0, 0, '#4CAF50'),
            ('Prepend', self.prepend_node, 0, 1, '#2196F3'),
            ('Delete', self.delete_node, 0, 2, '#f44336'),
            ('Search', self.search_node, 0, 3, '#FF9800'),
            ('Insert After', self.insert_node, 1, 0, '#9C27B0'),
            ('Reverse', self.reverse_list, 1, 1, '#00BCD4'),
            ('Count', self.count_nodes, 1, 2, '#FFC107'),
            ('Clear', self.clear_list, 1, 3, '#795548'),
        ]
        
        for text, func, row, col, color in buttons_data:
            btn = QPushButton(text)
            btn.setFont(QFont('Arial', 10, QFont.Bold))
            btn.setMinimumHeight(40)
            btn.clicked.connect(func)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 5px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {self.darken_color(color)};
                }}
                QPushButton:pressed {{
                    background-color: {self.darken_color(color, 40)};
                }}
            """)
            buttons_layout.addWidget(btn, row, col)
        
        buttons_group.setLayout(buttons_layout)
        main_layout.addWidget(buttons_group)
        
        # Output Group
        output_group = QGroupBox("Legacy Log")
        output_layout = QVBoxLayout()
        
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setMinimumHeight(150) # Reduced height since we have visuals
        self.output.setFont(QFont('Courier', 11))
        self.output.setStyleSheet("""
            QTextEdit {
                background-color: #f0f0f0;
                border: 2px solid #cccccc;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        output_layout.addWidget(self.output)
        output_group.setLayout(output_layout)
        main_layout.addWidget(output_group)
        
        central_widget.setLayout(main_layout)
    
    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ffffff;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
            }
            QLineEdit {
                border: 2px solid #cccccc;
                border-radius: 5px;
                padding: 5px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #2196F3;
            }
        """)
    
    def darken_color(self, hex_color, amount=20):
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[1:3], 16) - amount
        g = int(hex_color[3:5], 16) - amount
        b = int(hex_color[5:7], 16) - amount
        r = max(0, r)
        g = max(0, g)
        b = max(0, b)
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def append_node(self):
        try:
            data = int(self.input_field.text())
            self.mylist.append(data)
            self.canvas.animate_append(data) # Animation
            self.update_output(f"Appended {data}")
            self.input_field.clear()
        except ValueError:
            self.update_output("Error: Invalid input! Enter a number.")
    
    def prepend_node(self):
        try:
            data = int(self.input_field.text())
            self.mylist.prepend(data)
            self.canvas.animate_prepend(data) # Animation
            self.update_output(f"Prepended {data}")
            self.input_field.clear()
        except ValueError:
            self.update_output("Error: Invalid input! Enter a number.")
    
    def delete_node(self):
        try:
            data = int(self.input_field.text())
            
            # We need the index for the animation, so let's find it first
            index = -1
            temp = self.mylist.head
            idx = 0
            while temp:
                if temp.data == data:
                    index = idx
                    break
                temp = temp.next
                idx += 1
            
            if index != -1:
                self.mylist.delete_node(data)
                self.canvas.animate_delete(index) # Animation
                self.update_output(f"Deleted {data}")
            else:
                self.update_output(f"Node {data} not found for deletion.")
                
            self.input_field.clear()
        except ValueError:
            self.update_output("Error: Invalid input! Enter a number.")
    
    def search_node(self):
        try:
            data = int(self.input_field.text())
            result = self.mylist.search(data)
            
            # Simple highlight animation could be added here
            if result:
                self.update_output(f"Found {data} in the list!")
            else:
                self.update_output(f"{data} not found in the list.")
        except ValueError:
            self.update_output("Error: Invalid input! Enter a number.")
    
    def insert_node(self):
        try:
            data = int(self.input_field.text())
            key = int(self.key_field.text())
            
            # Find index of key
            index = -1
            temp = self.mylist.head
            idx = 0
            while temp:
                if temp.data == key:
                    index = idx
                    break
                temp = temp.next
                idx += 1
            
            if index != -1:
                self.mylist.insertion(data, key)
                # For now, just sync full list for insertion as it is complex to animate "insert in middle" right now
                # Or wait, let's keep it simple: sync
                self.canvas.sync_from_list(self.mylist)
                self.update_output(f"Inserted {data} after {key}")
            else:
                self.update_output(f"Key {key} not found.")

            self.input_field.clear()
            self.key_field.clear()
        except ValueError:
            self.update_output("Error: Invalid input! Enter numbers.")
    
    def reverse_list(self):
        self.mylist.reverse()
        self.canvas.sync_from_list(self.mylist) # Sync is easiest for full reverse
        self.update_output("List reversed!")
    
    def count_nodes(self):
        count = self.mylist.count()
        self.update_output(f"Total nodes: {count}")
    
    def clear_list(self):
        self.mylist.head = None
        self.canvas.clear_scene()
        self.update_output("List cleared!")
    
    def update_output(self, message):
        pass # Disabling text log spam for now or keep it minimal
        current = self.output.toPlainText()
        list_display = str(self.mylist) if str(self.mylist) else "Empty"
        
        if current:
            new_text = f"{current}\n{'─' * 60}\n✓ {message}\n📋 List: {list_display}"
        else:
            new_text = f"✓ {message}\n📋 List: {list_display}"
        
        self.output.setText(new_text)
        self.output.verticalScrollBar().setValue(self.output.verticalScrollBar().maximum())


mylist = LinkedList()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = LinkedListGUI(mylist)
    gui.show()
    sys.exit(app.exec_())
