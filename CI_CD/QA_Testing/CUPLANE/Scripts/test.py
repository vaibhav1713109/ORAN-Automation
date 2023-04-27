# Python program to implement the above approach
class Node:
	# constructor to initialize the node object
	def __init__(self, data):
		self.number = data
		self.next = None

class linked_list:
    def __init__(self) -> None:
        self.head = None
	
    def push(self,data):
        new_node = Node(data)
        new_node.next = self.head
        self.head = new_node


    def deleteN(self, key):
        temp = self.head
        if (temp is not None):
            if (temp.number == key):
                self.head = temp.next
                temp = None
                return
        while (temp is not None):
             if temp.number == key:
                  break
             prev = temp
             temp = temp.next

        if temp is None:
             return
        prev.next = temp.next
        temp = None


    def printList(self):
        print(self.head)
        while(self.head):
            if self.head.next == None:
                print("[", self.head.number, "] ", "[", hex(id(self.head)), "]->", "nil")
            else:
                print("[", self.head.number, "] ", "[", hex(
                    id(self.head)), "]->", hex(id(self.head.next)))
            self.head = self.head.next
        print("")
        print("")


llist = linked_list()
llist.push(7)
llist.push(1)
llist.push(3)
llist.push(2)
 
print("Created Linked List: ")
llist.printList()
llist.deleteN(1)
print("\nLinked List after Deletion of 1:")
llist.printList()

