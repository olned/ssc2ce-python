from ssc2ce.common import L2BookSide


class L2FundingBookSide(L2BookSide):

    def add_item(self, item: list):
        self.data.add(item)

    def update_item(self, item: list):
        price = item[0]
        count = item[2]
        key = -price if self.is_bids else price
        i = self.data.bisect_key_left(key)

        if 0 <= i < len(self.data):
            value = self.data[i]
        else:
            if count == 0:
                return False

            self.data.add(item)
            return True

        if count == 0:
            if value[0] == price:
                self.data.discard(value)
                return True
            else:
                return False

        if value[0] == price:
            self.data[i] = item
        else:
            self.data.add(item)
        return True

    def delete(self, price: float):
        return self.update_item([price, 0, 0, 0])
