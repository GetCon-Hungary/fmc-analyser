class AccessPolicy():
    def __init__(self, id, name, rules):
        self.name = name
        self.id = id
        self.rules = rules

    def enabled_rules_count(self):
        count = 0
        for rule in self.rules:
            if rule.enabled:
                count += 1
        return count
    
    def allowed_rules_count(self):
        count = 0
        for rule in self.rules:
            if str.lower(rule.action) == "allow":
                count += 1
        return count
    
    def allowed_rules_ratio(self):
        try:
            return (self.allowed_rules_count() / len(self.rules)) * 100
        except:
            return "NaN"
        
    def enabled_rules_ratio(self):
        try:
            return self.enabled_rules_count() / len(self.rules) * 100
        except:
            return "NaN"
