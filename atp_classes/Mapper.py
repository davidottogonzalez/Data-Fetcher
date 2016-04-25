class Mapper:
    __network_map = {}

    def __init__(self):
        self.__network_map = {
            "e!": "e! entertainment"
        }

    def map_netowrk(self, unmap_search):
        if unmap_search.lower() in self.__network_map:
            return self.__network_map[unmap_search.lower()]

        return unmap_search
