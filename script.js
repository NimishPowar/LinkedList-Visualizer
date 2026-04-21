/**
 * LinkView Premium Logic & Visualization
 */

class Node {
    constructor(value) {
        this.value = value;
        this.next = null;
        this.prev = null;
        this.id = `node-${Math.random().toString(36).substr(2, 9)}`;
    }
}

class LinkedList {
    constructor(type = 'singly') {
        this.head = null;
        this.tail = null;
        this.length = 0;
        this.type = type; // 'singly', 'doubly', 'circular'
    }

    append(value) {
        const newNode = new Node(value);
        if (!this.head) {
            this.head = newNode;
            this.tail = newNode;
        } else {
            newNode.prev = this.tail;
            this.tail.next = newNode;
            this.tail = newNode;
        }

        if (this.type === 'circular') {
            this.tail.next = this.head;
            this.head.prev = this.tail;
        }

        this.length++;
        return newNode;
    }

    prepend(value) {
        const newNode = new Node(value);
        if (!this.head) {
            this.head = newNode;
            this.tail = newNode;
        } else {
            newNode.next = this.head;
            this.head.prev = newNode;
            this.head = newNode;
        }

        if (this.type === 'circular') {
            this.tail.next = this.head;
            this.head.prev = this.tail;
        }

        this.length++;
        return newNode;
    }

    delete(value) {
        if (!this.head) return null;

        let current = this.head;
        let deletedNode = null;

        // Special case for circular or single node
        for (let i = 0; i < this.length; i++) {
            if (current.value === value) {
                deletedNode = current;
                break;
            }
            current = current.next;
            if (current === this.head) break;
        }

        if (!deletedNode) return null;

        if (deletedNode === this.head) {
            if (this.length === 1) {
                this.head = null;
                this.tail = null;
            } else {
                this.head = this.head.next;
                this.head.prev = this.tail;
                this.tail.next = this.head;
            }
        } else if (deletedNode === this.tail) {
            this.tail = this.tail.prev;
            this.tail.next = this.head;
            this.head.prev = this.tail;
        } else {
            deletedNode.prev.next = deletedNode.next;
            deletedNode.next.prev = deletedNode.prev;
        }

        this.length--;
        return deletedNode;
    }

    insertAfter(targetValue, newValue) {
        let current = this.head;
        for (let i = 0; i < this.length; i++) {
            if (current.value === targetValue) {
                const newNode = new Node(newValue);
                newNode.next = current.next;
                newNode.prev = current;
                
                if (current.next) {
                    current.next.prev = newNode;
                }
                current.next = newNode;

                if (current === this.tail) {
                    this.tail = newNode;
                    if (this.type === 'circular') {
                        this.tail.next = this.head;
                        this.head.prev = this.tail;
                    }
                }
                
                this.length++;
                return newNode;
            }
            current = current.next;
            if (current === this.head) break;
        }
        return null;
    }

    reverse() {
        if (!this.head || this.length <= 1) return;

        let current = this.head;
        let prev = null;
        let next = null;

        // Store original head and tail
        const oldHead = this.head;
        const oldTail = this.tail;

        for (let i = 0; i < this.length; i++) {
            next = current.next;
            current.next = prev;
            current.prev = next;
            prev = current;
            current = next;
        }

        this.head = oldTail;
        this.tail = oldHead;

        if (this.type === 'circular') {
            this.tail.next = this.head;
            this.head.prev = this.tail;
        } else {
            this.tail.next = null;
            this.head.prev = null;
        }
    }

    toArray() {
        const arr = [];
        let current = this.head;
        for (let i = 0; i < this.length; i++) {
            arr.push(current);
            current = current.next;
            if (current === this.head) break;
        }
        return arr;
    }
}

// --- Visualizer Controller ---

class Visualizer {
    constructor() {
        this.list = new LinkedList();
        this.svg = document.getElementById('visualizer-svg');
        this.container = document.getElementById('canvas-container');
        this.nodeRadius = 25;
        this.nodeSpacing = 120;
        this.startY = 200;
        this.startX = 60;
        this.currentOperation = null;
        
        this.initEventListeners();
        this.updateStats();
        this.render();
    }

    initEventListeners() {
        // Operations
        document.getElementById('append-btn').addEventListener('click', () => this.handleAppend());
        document.getElementById('prepend-btn').addEventListener('click', () => this.handlePrepend());
        document.getElementById('delete-btn').addEventListener('click', () => this.handleDelete());
        document.getElementById('insert-btn').addEventListener('click', () => this.handleInsert());
        document.getElementById('search-btn').addEventListener('click', () => this.handleSearch());
        document.getElementById('reverse-btn').addEventListener('click', () => this.handleReverse());
        document.getElementById('clear-btn').addEventListener('click', () => this.handleClear());

        // Type Toggles
        document.querySelectorAll('.type-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('.type-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                this.changeListType(btn.dataset.type);
            });
        });

        // Theme Toggle
        document.getElementById('theme-toggle').addEventListener('click', () => {
            document.body.classList.toggle('light-theme');
            const icon = document.querySelector('#theme-toggle i');
            icon.classList.toggle('fa-moon');
            icon.classList.toggle('fa-sun');
        });

        // Language Select
        document.getElementById('language-select').addEventListener('change', () => this.updateCodeSnippet(this.currentOperation));
    }

    handleAppend() {
        const val = document.getElementById('node-value').value;
        if (val === '') return;
        this.list.append(parseInt(val));
        this.render();
        this.updateStats();
        this.currentOperation = 'append';
        this.updateCodeSnippet('append', val);
        document.getElementById('node-value').value = '';
    }

    handlePrepend() {
        const val = document.getElementById('node-value').value;
        if (val === '') return;
        this.list.prepend(parseInt(val));
        this.render();
        this.updateStats();
        this.currentOperation = 'append'; // Prepend is similar to append logic-wise in many snippets
        this.updateCodeSnippet('append', val);
        document.getElementById('node-value').value = '';
    }

    handleDelete() {
        const val = document.getElementById('node-value').value;
        if (val === '') return;
        this.list.delete(parseInt(val));
        this.render();
        this.updateStats();
        this.currentOperation = 'delete';
        this.updateCodeSnippet('delete', val);
    }

    handleInsert() {
        const val = document.getElementById('node-value').value;
        const target = document.getElementById('target-value').value;
        if (val === '' || target === '') return;
        this.list.insertAfter(parseInt(target), parseInt(val));
        this.render();
        this.updateStats();
        this.updateCodeSnippet('insert', val, target);
    }

    handleSearch() {
        const val = parseInt(document.getElementById('node-value').value);
        if (isNaN(val)) return;
        
        const nodes = this.list.toArray();
        let i = 0;
        const interval = setInterval(() => {
            if (i >= nodes.length) {
                clearInterval(interval);
                return;
            }
            
            const nodeEl = document.getElementById(nodes[i].id);
            const circle = nodeEl.querySelector('.node-circle');
            circle.style.fill = '#f59e0b'; // Highlight color
            
            if (nodes[i].value === val) {
                circle.style.fill = '#10b981'; // Found color
                clearInterval(interval);
                this.updateCodeSnippet('search', val);
            } else {
                setTimeout(() => {
                    circle.style.fill = '';
                }, 400);
            }
            i++;
        }, 500);
    }

    handleReverse() {
        this.list.reverse();
        this.render();
        this.updateStats();
        this.currentOperation = 'reverse';
        this.updateCodeSnippet('reverse');
    }

    handleClear() {
        this.list = new LinkedList(this.list.type);
        this.render();
        this.updateStats();
        this.updateCodeSnippet('clear');
    }

    changeListType(type) {
        // Re-initialize list with new type but keep current data if possible
        const oldData = this.list.toArray().map(n => n.value);
        this.list = new LinkedList(type);
        oldData.forEach(val => this.list.append(val));
        this.render();
        this.updateStats();
        this.updateCodeSnippet(this.currentOperation);
    }

    updateStats() {
        document.getElementById('stat-length').textContent = this.list.length;
        document.getElementById('stat-head').textContent = this.list.head ? this.list.head.value : 'NULL';
        document.getElementById('stat-tail').textContent = this.list.tail ? this.list.tail.value : 'NULL';
        
        let complexity = 'O(1)';
        if (this.list.length > 0) {
            complexity = 'O(n)'; // General search/access
        }
        document.getElementById('stat-complexity').textContent = complexity;
    }

    updateCodeSnippet(operation = '', val = '', target = '') {
        const lang = document.getElementById('language-select').value;
        const display = document.getElementById('code-display');
        const listType = this.list.type;
        
        const snippets = {
            python: {
                singly: {
                    append: `def append(self, data):\n    new_node = Node(data)\n    if not self.head:\n        self.head = new_node\n        return\n    last = self.head\n    while last.next:\n        last = last.next\n    last.next = new_node`,
                    delete: `def delete(self, key):\n    temp = self.head\n    if temp and temp.data == key:\n        self.head = temp.next\n        return\n    prev = None\n    while temp and temp.data != key:\n        prev = temp\n        temp = temp.next\n    if not temp: return\n    prev.next = temp.next`
                },
                doubly: {
                    append: `def append(self, data):\n    new_node = Node(data)\n    if not self.head:\n        self.head = new_node\n        return\n    new_node.prev = self.tail\n    self.tail.next = new_node\n    self.tail = new_node`,
                    delete: `def delete(self, node):\n    if node.prev: node.prev.next = node.next\n    if node.next: node.next.prev = node.prev\n    if node == self.head: self.head = node.next`
                },
                circular: {
                    append: `def append(self, data):\n    new_node = Node(data)\n    if not self.head:\n        self.head = new_node\n        new_node.next = self.head\n        return\n    self.tail.next = new_node\n    new_node.next = self.head\n    self.tail = new_node`,
                    delete: `def delete(self, key):\n    # Search and unlink, then ensure tail.next = head\n    self.tail.next = self.head`
                }
            },
            javascript: {
                singly: {
                    append: `append(val) {\n    const node = new Node(val);\n    if (!this.head) {\n        this.head = node;\n        return;\n    }\n    let curr = this.head;\n    while (curr.next) curr = curr.next;\n    curr.next = node;\n}`,
                    reverse: `reverse() {\n    let prev = null, curr = this.head;\n    while (curr) {\n        let next = curr.next;\n        curr.next = prev;\n        prev = curr;\n        curr = next;\n    }\n    this.head = prev;\n}`
                },
                doubly: {
                    append: `append(val) {\n    const node = new Node(val);\n    node.prev = this.tail;\n    if (this.tail) this.tail.next = node;\n    this.tail = node;\n}`
                }
            },
            cpp: {
                singly: {
                    append: `void append(int val) {\n    Node* newNode = new Node(val);\n    if (head == nullptr) { head = newNode; return; }\n    Node* temp = head;\n    while (temp->next != nullptr) temp = temp->next;\n    temp->next = newNode;\n}`
                },
                doubly: {
                    append: `void append(int val) {\n    Node* newNode = new Node(val);\n    newNode->prev = tail;\n    if (tail) tail->next = newNode;\n    tail = newNode;\n}`
                }
            }
        };

        // Fallback to singly logic if specific type logic isn't defined for a language
        const langData = snippets[lang];
        let code = "";
        
        if (operation) {
            const typeLogic = langData[listType] || langData['singly'];
            code = typeLogic[operation] || langData['singly'][operation] || `# Logic for ${operation} in ${lang} coming soon!`;
        } else {
            code = "# Select an operation to see logic";
        }
        
        display.textContent = code;
    }

    render() {
        // Clear SVG
        const nodesContainer = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        const arrowsContainer = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        
        // Remove existing dynamic content
        const children = Array.from(this.svg.children);
        children.forEach(child => {
            if (child.tagName !== 'defs') this.svg.removeChild(child);
        });

        this.svg.appendChild(arrowsContainer);
        this.svg.appendChild(nodesContainer);

        const nodes = this.list.toArray();
        
        // Update SVG width and viewBox
        const requiredWidth = Math.max(1000, (nodes.length + 1) * this.nodeSpacing + 100);
        this.svg.setAttribute('width', requiredWidth);
        this.svg.setAttribute('viewBox', `0 0 ${requiredWidth} 400`);

        nodes.forEach((node, index) => {
            const x = this.startX + index * this.nodeSpacing;
            const y = this.startY;

            // Create Node Group
            const group = document.createElementNS('http://www.w3.org/2000/svg', 'g');
            group.setAttribute('id', node.id);
            group.setAttribute('class', 'node-group new');
            group.setAttribute('transform', `translate(${x}, ${y})`);

            // Circle
            const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            circle.setAttribute('class', 'node-circle');
            circle.setAttribute('r', this.nodeRadius);
            group.appendChild(circle);

            // Text
            const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            text.setAttribute('class', 'node-text');
            text.setAttribute('text-anchor', 'middle');
            text.setAttribute('dy', '.3em');
            text.textContent = node.value;
            group.appendChild(text);

            // Label (Index)
            const label = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            label.setAttribute('fill', 'var(--text-muted-dark)');
            label.setAttribute('font-size', '10px');
            label.setAttribute('font-weight', '600');
            label.setAttribute('text-anchor', 'middle');
            label.setAttribute('y', this.nodeRadius + 22);
            label.textContent = index === 0 ? 'HEAD' : (index === nodes.length - 1 ? 'TAIL' : `NODE ${index}`);
            group.appendChild(label);

            nodesContainer.appendChild(group);

            // Create Arrow to Next
            if (node.next && (this.list.type !== 'circular' || index < nodes.length - 1)) {
                this.drawArrow(arrowsContainer, x + this.nodeRadius, y, x + this.nodeSpacing - this.nodeRadius, y);
            }

            // Draw Doubly pointers
            if (this.list.type === 'doubly' && node.prev && index > 0) {
                 this.drawArrow(arrowsContainer, x - this.nodeRadius, y + 5, x - this.nodeSpacing + this.nodeRadius, y + 5, true);
            }

            // Draw Circular back arrow
            if (this.list.type === 'circular' && index === nodes.length - 1 && nodes.length > 1) {
                this.drawCircularArrow(arrowsContainer, x, y, this.startX, y);
            }
        });

        // If empty
        if (nodes.length === 0) {
            const emptyText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            emptyText.setAttribute('x', '50%');
            emptyText.setAttribute('y', '50%');
            emptyText.setAttribute('text-anchor', 'middle');
            emptyText.setAttribute('fill', 'var(--text-muted-dark)');
            emptyText.setAttribute('font-size', '20px');
            emptyText.textContent = 'List is empty. Add a node to begin.';
            this.svg.appendChild(emptyText);
        }
    }

    drawArrow(container, x1, y1, x2, y2, isBack = false) {
        const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        // If it's a back arrow (doubly), offset it vertically
        const offset = isBack ? 10 : -5;
        
        line.setAttribute('x1', x1);
        line.setAttribute('y1', y1 + offset);
        line.setAttribute('x2', x2);
        line.setAttribute('y2', y2 + offset);
        line.setAttribute('stroke', isBack ? 'var(--secondary)' : 'var(--primary)');
        line.setAttribute('stroke-width', '2.5');
        line.setAttribute('marker-end', isBack ? 'url(#arrowhead-back)' : 'url(#arrowhead)');
        line.style.transition = 'all 0.5s ease';
        line.style.opacity = '0.9';
        container.appendChild(line);
    }

    drawCircularArrow(container, x1, y1, x2, y2) {
        const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        const bend = 80;
        // Curve from bottom of last node back to top of first node
        const d = `M ${x1} ${y1 + this.nodeRadius} C ${x1} ${y1 + bend}, ${x2} ${y2 + bend}, ${x2} ${y2 + this.nodeRadius}`;
        path.setAttribute('d', d);
        path.setAttribute('fill', 'none');
        path.setAttribute('stroke', 'var(--accent)');
        path.setAttribute('stroke-width', '2.5');
        path.setAttribute('stroke-dasharray', '5,5');
        path.setAttribute('marker-end', 'url(#arrowhead)');
        path.style.opacity = '0.7';
        container.appendChild(path);
    }
}

// Initialize on load
window.addEventListener('DOMContentLoaded', () => {
    window.visualizer = new Visualizer();
});
