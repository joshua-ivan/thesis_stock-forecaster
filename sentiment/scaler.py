from sklearn.preprocessing import MinMaxScaler
import numpy


class SentimentScaler:
    neg_scaler = MinMaxScaler(feature_range=(-2, 0))
    pos_scaler = MinMaxScaler(feature_range=(0, 2))

    def format_values(self, v):
        return numpy.array(v).reshape(-1, 1)

    def fit_transform(self, raw_scores):
        pos_scores = [s for s in raw_scores if s > 0]
        pos_scores.append(0)
        self.pos_scaler.fit_transform(self.format_values(pos_scores))

        neg_scores = [s for s in raw_scores if s < 0]
        neg_scores.append(0)
        self.neg_scaler.fit_transform(self.format_values(neg_scores))

    def transform(self, raw_score):
        formatted_value = self.format_values(raw_score)
        if raw_score > 0:
            return self.pos_scaler.transform(formatted_value)
        elif raw_score < 0:
            return self.neg_scaler.transform(formatted_value)
        else:
            return 0
