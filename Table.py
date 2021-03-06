import time
import random
from typing import Dict, List


class Option:
    def __init__(self, destination, distance, learned_from=None):
        """
        Init a option for a route. It can be obtained by adding a link
        or learning from another router.
        :param destination: Router destination IP address.
        :type destination: str
        :param distance: Distance from local router to destination router.
        :type distance: int
        :param learned_from: Router destination IP address which was learned.
        :type learned_from: str
        """
        self.destination = destination
        self.distance = distance
        self.timestamp = time.time()
        self.learned_from = learned_from


class Route:
    options: List[Option]

    def __init__(self, is_link=False):
        self.tie = None
        self.min = None
        self.is_link = is_link
        self.options = []

    def sort_options(self):
        """
        Sort options by distance and count the number os options with the shortest distance.
        """
        if len(self.options) == 0:
            self.tie = None
            self.min = None
        else:
            self.options.sort(key=lambda option: option.distance)
            self.min = self.options[0].distance
            self.tie = sum(option.distance == self.min for option in self.options)
    
    def add_learned_router(self, destination, distance, learned_from):
        """
        Add a learned router from update.
        :param destination: Router destination IP address.
        :type destination: str
        :param distance: Distance from local router to destination router.
        :type distance: int
        :param learned_from: Router from which the route was learned.
        :type learned_from: str
        """
        option = Option(destination=destination, distance=distance, learned_from=learned_from)
        if len(self.options) == 0:
            self.options.append(option)
            self.tie = 1
            self.min = distance
        elif len(self.options) > 0:
            for i in range(len(self.options)):
                if self.options[i].destination == destination and self.options[i].learned_from == learned_from:
                    self.options[i] = option
                    self.sort_options()
                    return
            self.options.append(option)
            self.sort_options()

    def add_link(self, destination, distance, learned_from=None):
        """
        Add a link on the router to another router
        :param destination: Router destination IP address.
        :type destination: str
        :param distance: Distance from local router to destination router.
        :type distance: int
        """
        for i in range(len(self.options)):
            if self.options[i].destination == destination:
                print("Router already added.")
                return

        option = Option(destination=destination, distance=distance, learned_from=learned_from)
        if len(self.options) == 0:
            self.options.append(option)
            self.tie = 1
            self.min = distance
        elif len(self.options) > 0:
            self.options.append(option)
            self.sort_options()


class Table:
    routes: Dict[str, Route]

    def __init__(self):
        self.routes = {}

    def add_link(self, destination, distance):
        """
        Store information about a link between to routers
        :param destination: Router destination IP address.
        :type destination: str
        :param distance: Distance from local router to destination router.
        :type distance: int
        :return:
        """
        if destination not in self.routes:
            self.routes[destination] = Route(is_link=True)
        self.routes[destination].add_link(destination, distance)

    def add_learned_router(self, destination, distance, learned_from):
        """
        Store information about a learned router coming from an update message
        """
        if destination not in self.routes:
            self.routes[destination] = Route()
        self.routes[destination].add_learned_router(learned_from, distance, learned_from)

    def del_link(self, router):
        """
        Delete a link and all routes learned by it.
        :param router: Router address do to be deleted.
        :type router: str
        """
        if router not in self.routes:
            print('Router ' + str(router) + ' not found.')
        elif self.routes[router].is_link:
            print("Router is link.")
            for key in self.routes.keys():
                for indexOption, option in enumerate(self.routes[key].options):
                    if option.destination == router:
                        self.routes[key].is_link = False
                        del self.routes[key].options[indexOption]
                        self.routes[key].sort_options()
                # if len(self.routes[key].options) == 0:
                #     del self.routes[key]
                # else:
            self.routes = {addr: route for addr, route in self.routes.items() if len(route.options) > 0}
            print("Delete complete.")
        else:
            print("Router is not a direct link.")

    def get_destination_by_routes(self, destination):
        """
        Return router address to send the next packet and update to next router in case of tie on its distances.
        :param destination: Router destination IP address.
        :type destination: str
        :return: Router IP address to send the next packet.
        :rtype: str
        """
        index = random.randrange(self.routes[destination].tie)
        addr = self.routes[destination].options[index].destination
        return addr

    def to_string(self):
        """
        Create a formatted table with all routes.
        :return: String formatted
        :rtype: str
        """
        string = ""
        for addr, route in self.routes.items():
            string += "Routes to " + addr + "\n"
            string += "Tie on first " + str(route.tie) + " options\n"
            string += "Minimum distance: " + str(route.min) + "\n"
            destination_max_len = len("Destination")
            distance_max_len = len("Distance")
            timestamp_max_len = len("Timestamp")
            learned_from_max_len = len("Learned from")
            for option in route.options:
                if len(option.destination) > destination_max_len:
                    destination_max_len = len(option.destination)
                if len(str(option.distance)) > distance_max_len:
                    distance_max_len = len(str(option.distance))
                if len(str(option.timestamp)) > timestamp_max_len:
                    timestamp_max_len = len(str(option.timestamp))
                if len(str(option.learned_from)) > learned_from_max_len:
                    learned_from_max_len = len(str(option.learned_from))
            string += "┌─" + (destination_max_len + 3) * "─" + (distance_max_len + 3) * "─" + (timestamp_max_len + 3) * "─" + (
                              learned_from_max_len + 1) * "─" + "┐\n"
            string += "│ Destination" + (destination_max_len - len("Destination") + 1) * " " + "│ Distance" + (
                    distance_max_len - len("Distance") + 1) * " " + "│ Timestamp" + (
                              timestamp_max_len - len("Timestamp") + 1) * " " + "│ Learned from" + (
                              learned_from_max_len - len("Learned from") + 1) * " " + "│\n"
            for option in route.options:
                string += "│ " + (destination_max_len - len(option.destination)) * " " + option.destination + " │ " + (
                        distance_max_len - len(str(option.distance))) * " " + str(option.distance) + " │ " + (
                                  timestamp_max_len - len(str(option.timestamp))) * " " + str(
                    option.timestamp) + " │ " + (
                                  learned_from_max_len - len(str(option.learned_from))) * " " + str(
                    option.learned_from) + " │\n"
            string += "└─" + (destination_max_len + 3) * "─" + (distance_max_len + 3) * "─" + (timestamp_max_len + 3) * "─" + (
                              learned_from_max_len + 1) * "─" + "┘\n"
        if string == "":
            string += "There are no routes."
        return string
