from google.appengine.ext import ndb


class Positions(ndb.Model):
    uid = ndb.StringProperty()
    stock = ndb.StringProperty()
    position = ndb.PickleProperty()
    vols = ndb.PickleProperty()
    rate = ndb.FloatProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)

    @staticmethod
    def save_position(uid, stock, position, vols, rate):
        this_pos = Positions().retrieve_position(uid, stock)
        if this_pos:
            this_pos.position = position
            this_pos.vols = vols
            this_pos.rate = rate
            position_key = this_pos.put()
        else:
            pos = Positions(uid=uid,
                            stock=stock,
                            position=position,
                            vols=vols,
                            rate=rate)
            position_key = pos.put()
        return position_key

    @staticmethod
    def retrieve_position(uid, stock):
        position = Positions.query(Positions.uid == uid, Positions.stock == stock).order(-Positions.created)
        if position.count() > 0:
            for p in position:
                return p
        return False


class OptionChain(ndb.Model):
    stock = ndb.StringProperty()
    option_chain = ndb.PickleProperty()
    created = ndb.DateTimeProperty(auto_now=True)

    @staticmethod
    def save_option_chain(stock, option_chain):
        chain = OptionChain(stock=stock,
                            option_chain=option_chain)
        chain_key = chain.put()
        return chain_key

    @staticmethod
    def retrieve_option_chain(stock):
        chain = OptionChain.query(OptionChain.stock == stock)
        if chain.count() > 0:
            for c in chain:
                return c
        return False