
class PairwiseEvaluation(object):
    def __init__(self,x,true,predicted):
        self.sums = dict()
        for key in ["true positives","false positives","true negatives", "false negatives"]:
            self.sums[key] = 0
        for x1,true1,pred1 in zip(x,true,predicted):
            for x2,true2,pred2 in zip(x,true,predicted):
                if true1 == true2 and pred1 == pred2:
                    if "true positives" not in self.sums:
                        self.sums["true positives"] =0
                    self.sums["true positives"]+=1
                if true1 != true2 and pred1 == pred2:
                    if "false positives" not in self.sums:
                        self.sums["false positives"] =0
                    self.sums["false positives"]+=1
                if true1 == true2 and pred1 != pred2:
                    if "false negatives" not in self.sums:
                        self.sums["false negatives"] =0
                    self.sums["false negatives"]+=1
                if true1 != true2 and pred1 != pred2:
                    if "true negatives" not in self.sums:
                        self.sums["true negatives"] =0
                    self.sums["true negatives"]+=1
    def getPrecisionRecallF1(self):
        precision = self.sums["true positives"]/(self.sums["true positives"]+self.sums["false positives"])
        recall = self.sums["true positives"]/(self.sums["true positives"]+self.sums["false negatives"])
        return (precision,
                recall,
                2 * (precision*recall)/(precision+recall)
                )
