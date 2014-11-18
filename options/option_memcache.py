from google.appengine.api import memcache
import occ_query as OCC


class OptionsMemcache:
    def __init__(self, user, stock_symbol):
        self.user = user
        self.stock_symbol = stock_symbol
        self.optionable_type = 'optionable_list'
        self.option_chain_type = self.stock_symbol + '_option_chain'
        self.optionable_list = self.get_optionable_list()
        self.option_chain = None

        if self.stock_symbol in self.optionable_list:
            self.option_chain = self.get_option_chain()

    def get_optionable_list(self):
        optionable = memcache.get(self.optionable_type)
        if not optionable:
            optionable = OCC.OccOptionableList().optionable_list
            if optionable:
                memcache.set(self.optionable_type, optionable, 25200)
        return optionable

    def make_memcache_string(self, its_type):
        return self.user + '_' + self.stock_symbol + '_' + its_type

    def get_user_type(self, its_type):
        return memcache.get(self.make_memcache_string(its_type))

    def put_user_of_type(self, value, its_type):
        memcache.set(self.make_memcache_string(its_type), value, 25200)

    def get_option_chain(self):
        option_chain = memcache.get(self.option_chain_type)
        if option_chain:
            return option_chain
        else:
            option_chain = OCC.OccOptionChain(self.stock_symbol)
            self.put_option_chain(option_chain)
            return option_chain

    def put_option_chain(self, option_chain):
        memcache.set(self.option_chain_type, option_chain, 25200)

    def remove_user_position(self):
        for key, value in self.types.items():
            memcache.delete(self.make_memcache_string(value))