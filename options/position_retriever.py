import option_memcache as OM
import option_db as ODB
import occ_query as OCC
import yahoo_query as YQ


class PositionRetriever:
    def __init__(self, user, stock_symbol):
        self.user = user
        self.stock_symbol = stock_symbol.upper()
        self.optionable_list = None
        self.position = None
        self.vols = None
        self.vols_str = None
        self.projected_dividends = None
        self.past_dividends = None
        self.option_chain = None
        self.got_past_div = None
        self.stock_price = None
        self.has_error = False

        mem_pos = OM.OptionsMemcache(self.user, self.stock_symbol)
        if self.stock_symbol not in mem_pos.optionable_list:
            self.has_error = True
        else:
            yq = YQ.YahooQuery()
            self._get_from_memcache(mem_pos)  # get option chain and optionable list from memcache
            self._make_empty_position()  # make empty stock position
            self.past_dividends, self.got_past_div = yq.get_dividend(self.stock_symbol)  # make divs come up with better
            if self.got_past_div:
                #self.mem_pos.put_user_of_type(self.past_dividends, self.mem_pos.past_dividends_type)
                self.projected_dividends = yq.create_div_projections(self.past_dividends)
                #self.mem_pos.put_user_of_type(self.projected_dividends, self.mem_pos.projected_dividends_type)
            self.stock_price = yq.stock_px(self.stock_symbol)
            if not self.stock_price:
                self.stock_price = 50.00
            self._make_blank_vols()  # make generic vols
            self.rate = .005

            self._get_position_from_db()
            self._make_vol_str()

    def _make_blank_vols(self):
        self.vols = {}
        for exp in self.option_chain.ordered_expirations_list:
                    self.vols[exp] = [.4, 0, 0]

    def _get_from_memcache(self, mem_pos):
        self.optionable_list = mem_pos.optionable_list
        self.option_chain = mem_pos.option_chain

    def _get_option_chain_from_occ(self):
        self.option_chain = OCC.OccOptionChain(self.stock_symbol)

    def _make_empty_position(self):
        #make assertion here
        self.position = {'stock': 0}
        for option in self.option_chain.option_chain:
            self.position[option] = 0

    def _get_position_from_db(self):
        p = ODB.Positions().retrieve_position(self.user, self.stock_symbol)
        if p:
            db_position = p.position
            db_vols = p.vols
            self.rate = p.rate
            self._fix_db_position(db_position)
            self._fix_db_vols(db_vols)

    def _fix_db_position(self, db_position):
        for option in self.position:
            if option in db_position:
                self.position[option] = db_position[option]

    def _fix_db_vols(self, db_vols):
        for date in self.vols:
            if date in db_vols:
                self.vols[date] = db_vols[date]

    def _make_vol_str(self):
        self.vols_str = {}
        for i in range(len(self.option_chain.ordered_expirations_list)):
            self.vols_str[self.option_chain.ordered_expirations_string[i]] = \
                self.vols[self.option_chain.ordered_expirations_list[i]]