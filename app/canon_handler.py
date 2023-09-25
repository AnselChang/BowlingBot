import json, os

class Message:
    def __init__(self, channelID, messageIDs):
        self.channelID = channelID
        self.messageIDs = messageIDs

class CanonData:

    def __init__(self) -> None:
        self.rosterMessages: list[Message] = []
        self.lineupMessages: list[Message] = []

def loadCanonData() -> CanonData:

    if not os.path.exists("canon_data.json"):
        return CanonData()

    with open("canon_data.json", "r") as f:
        data = json.load(f)
        canonData = CanonData()
        for messageData in data["rosterMessageIDs"]:
            canonData.rosterMessages.append(Message(messageData["channelID"], messageData["messageIDs"]))

        for messageData in data["lineupMessageIDs"]:
            canonData.lineupMessages.append(Message(messageData["channelID"], messageData["messageIDs"]))    

    return canonData

def saveCanonData(data: CanonData):
    with open("canon_data.json", "w") as f:
        
        rosterMessageIDs = []
        for message in data.rosterMessages:
            rosterMessageIDs.append({"channelID": message.channelID, "messageIDs": message.messageIDs})

        lineupMessageIDs = []
        for message in data.lineupMessages:
            lineupMessageIDs.append({"channelID": message.channelID, "messageIDs": message.messageIDs})

        json.dump({"rosterMessageIDs": rosterMessageIDs, "lineupMessageIDs": lineupMessageIDs}, f, indent=4)
