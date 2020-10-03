# コーパスのデータベース。　会話のペアを蓄える。
class CorpusDatabase:
    def __init__(self):
        self.pairs = []
        self.pair_num = 0
    
    def add_pairs(self, pairs):
        # データベースに登録。
        for pair in pairs:
            self.pairs.append(pair)
            self.pair_num += 1