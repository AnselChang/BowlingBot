from enums import Transport

class BowlerDisplayInfo:

    def __init__(self, fullName: str, discord: str, transport: Transport):
        self.fullName = fullName
        self.discord = discord
        self.transport = transport

    def toString(self, absent: bool = False, showSub: bool = False) -> str:

        response = "(SUB) " if showSub else ""

        if absent:
            response += f"~~{self.fullName}~~"
        else:
            response += f"{self.fullName}"
            
        response += f" <@{self.discord}>"

        if not absent and self.transport == Transport.SELF:
            response += " (NOT BUS)"
        
        return response + "\n"