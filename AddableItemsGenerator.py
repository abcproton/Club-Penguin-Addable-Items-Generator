import json
import collections 
import urllib2

from time import sleep
from random import randint
from twisted.internet import task

from Penguin.Penguin import Penguin
from Penguin.ClubPenguin import ClubPenguin
from Penguin.ClubPenguin import PenguinFactory

class MyPenguin(Penguin):
    
    def __init__(self, player, items):
        super(MyPenguin, self).__init__(player)
        
        self.items = items
        self.file = open("AddableItemID.txt", "a")
        
        self.addListener("jr", self.handleJoinRoom)
        self.addListener("ai", self.handleAddItem)
        self.addListener("e", self.handleError)

    def handleJoinRoom(self, data):
        random = task.LoopingCall(self.sendPosition, randint(0,100), randint(0,100))
        random.start(20)
        
        heartbeat = task.LoopingCall(self.sendXt, "s", "u#h")
        heartbeat.start(30)
        
        self.buyInventory(self.items.popleft())
        
    def handleAddItem(self, data):
        print "ITEM ID -> " + data[3] + " succesfully added to inventory!"
        self.file.write(data[3] + "\n")

        self.buyInventory(self.items.popleft())
        sleep(3)
           
    def handleError(self, data):
        print data[3]
        if data[3] == "400" or data[3] == "408" or data[3] == "402" or data[3] == "410":
            itemID = self.items.popleft()
            print "ITEM ID -> " + str(itemID) + " failed to add to the inventory! (ERROR: " + data[3] + ")"
            self.buyInventory(itemID)
            sleep(3)
        
    
class AddableItemsFactory(PenguinFactory):
    
    def __init__(self, items):
        super(AddableItemsFactory, self).__init__()

        self.items = items
        
    def buildProtocol(self, addr):
        player = self.queue.pop()
        
        penguin = MyPenguin(player, self.items)
        
        return penguin


url = "http://media1.clubpenguin.com/play/en/web_service/game_configs/paper_items.json"
json_ = urllib2.urlopen(url).read()
items_list = json.loads(json_)
items = collections.deque()

for item in items_list:
    if "is_bait" not in item and "is_epf" not in item and item["is_member"] == False:
            items.append(item["paper_item_id"])

cp = ClubPenguin()

cp.connect(username="coolworld26", password="kartheyan2001", server="Permafrost", \
           factory=AddableItemsFactory(items))

cp.start()

