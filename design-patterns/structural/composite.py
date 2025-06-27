from abc import ABC, abstractmethod
from typing import List


# Component interface
class FileSystemComponent(ABC):
    @abstractmethod
    def show_details(self, indent: str = "") -> None:
        pass

    @abstractmethod
    def get_size(self) -> int:
        pass


# Leaf: Represents a file
class File(FileSystemComponent):
    def __init__(self, name: str, size: int):
        self.name = name
        self._size = size

    def show_details(self, indent: str = "") -> None:
        print(f"{indent}📄 {self.name} ({self._size} KB)")

    def get_size(self) -> int:
        return self._size


# Composite: Represents a directory
class Directory(FileSystemComponent):
    def __init__(self, name: str):
        self.name = name
        self._children: List[FileSystemComponent] = []

    def add(self, component: FileSystemComponent) -> None:
        self._children.append(component)

    def remove(self, component: FileSystemComponent) -> None:
        self._children.remove(component)

    def show_details(self, indent: str = "") -> None:
        print(f"{indent}📁 {self.name} (total: {self.get_size()} KB)")
        for child in self._children:
            child.show_details(indent + "    ")

    def get_size(self) -> int:
        return sum(child.get_size() for child in self._children)


# Client code
if __name__ == "__main__":
    print("File System Structure:")

    # Create files
    file1 = File("document.txt", 100)
    file2 = File("image.jpg", 250)
    file3 = File("notes.txt", 50)
    file4 = File("video.mp4", 1200)

    # Create directories
    root = Directory("Root")
    documents = Directory("Documents")
    media = Directory("Media")
    videos = Directory("Videos")

    # Build the tree structure
    documents.add(file1)
    documents.add(file3)

    videos.add(file4)

    media.add(file2)
    media.add(videos)

    root.add(documents)
    root.add(media)

    # Display the structure
    root.show_details()

    # Demonstrate uniform treatment
    print("\nTreating components uniformly:")
    components = [file1, documents]
    for component in components:
        component.show_details()
        print(f"Size: {component.get_size()} KB\n")

    """Key Features
Component Interface: Common interface (FileSystemComponent) for both leaf and composite objects

Leaf Objects: Basic elements that have no children (File)

Composite Objects: Containers that can hold leaves or other composites (Directory)

Uniform Treatment: Clients can treat individual files and entire directories the same way

Real-World Applications
GUI Components: Widget containers that can hold other widgets

Organization Structures: Departments containing sub-departments and employees

Graphics Systems: Shapes that can contain other shapes

Menu Systems: Menu items that can contain sub-menus

Benefits
Simplifies client code that can treat composites and individual objects uniformly

Makes it easy to add new component types

Provides a flexible structure that can represent complex hierarchies



1.Goal treating individual and aggregate objects uniformly
2. Objects use other objects properties/members through inheritance and composition
3. Composition lets us make compound objects

composite design pattern is used to treat both single and composite objects uniformly
    
"""


class GraphicObject:
    def __init__(self, color=None):
        self.color = color
        self.children = []
        self._name = 'Group'


    @property
    def name(self):
        return self._name


    def _print(self, items, depth):
        items.append('*' * depth)
        if self.color:
            items.append(self.color)
        items.append(f"{self.name}\n")

        for child in self.children:
            child._print(items, depth+1)

    def __str__(self):
        items = []
        self._print(items, 0)
        return ''.join(items)



class Circle(GraphicObject):
    @property
    def name(self):
        return 'Circle'


class Square(GraphicObject):
    @property
    def name(self):
        return 'Circle'


if  __name__ == '__main__':
    drawing = GraphicObject()
    drawing._name= 'My Drawing'
    drawing.children.append(Square('Red'))
    drawing.children.append(Square('Blue'))

    group = GraphicObject()
    group.children.append(Circle('Blue'))
    group.children.append(Square('Red'))

    drawing.children.append(group)
    print(drawing)
