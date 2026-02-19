class MockOracle:
    def __init__(self):
        self.history = []

    def predict(self, current_val):
        self.history.append(current_val)
        if len(self.history) > 20:
            self.history.pop(0)
            
        if len(self.history) < 3: return "STABLE", current_val
        
        # Simple Linear Extrapolation
        # predicted = current + (current - prev)
        trend = self.history[-1] - self.history[-2]
        predicted_val = self.history[-1] + trend
        
        # Dampen or exaggerate
        if trend > 5:
            predicted_val += trend * 0.5 # Exaggerate spikes
            
        status = "STABLE"
        if trend > 10:
            status = "CRITICAL_SPIKE_PREDICTED"
            
        return status, predicted_val
