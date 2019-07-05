import asyncio
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from stationary_agent import StationaryAgent
import util


class ScanBehaviour(CyclicBehaviour):
    def __init__(self, name, timeline):
        super().__init__()
        self.name = name
        self.timeline = timeline

        self.detected = False
        self.object = None
        self.object_id = None
        self.type = None
        self.at_x = None
        self.at_y = None

    async def on_start(self):
        print("[RADAR] ({}) start scanning...".format(self.name))
        # self.counter = 0

    async def run(self):
        data = self.timeline.next()
        if not data:
            return

        # print("{} scanning at: {}".format(self.name, self.counter))
        # self.counter += 1

        if data['type'] == 'enemy':
            self.detected = True
            self.object = data['object']
            self.object_id = data['id']
            self.type = data['type']
            self.at_x = data['x']
            self.at_y = data['y']
        else:
            self.detected = False

        if self.detected:
            if util.circle_contains(0, 0, 10, self.at_x, self.at_y):   # To HQ directly order missile to fire
                await self.send_message('missile1@xmpp.test')
                await self.send_message('missile2@xmpp.test')
                print("[RADAR] ({}) directly sent messages missiles".format(self.name))
            else:
                await self.send_message("hq@xmpp.test")
                print("[RADAR] ({}) sent message to HQ".format(self.name))

        await asyncio.sleep(2)

    async def send_message(self, to):
        msg = Message(to=to)  # Instantiate the message
        msg.set_metadata("performative", "inform")  # Set the "inform" FIPA performative
        msg.body = '{0}|{1}|{2}|{3}|{4}'.format(self.object, str(self.object_id), self.type, str(self.at_x),
                                                str(self.at_y))  # Set the message content

        await self.send(msg)


class RadarAgent(StationaryAgent):

    def __init__(self, aid, timeline):
        super().__init__(aid)

        self.timeline = timeline

    async def setup(self):
        print("[RADAR] ({}) starting...".format(self.aid))
        b = ScanBehaviour(self.aid, self.timeline)
        self.add_behaviour(b)
