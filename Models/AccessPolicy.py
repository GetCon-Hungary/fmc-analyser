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
    
    def calculate_avg_source_network_size_of_acp(self):
        number_of_ip_addresses = 0
        if len(self.rules) > 0:
            for rule in self.rules:
                number_of_ip_addresses += rule.get_source_network_size()
            return number_of_ip_addresses / len(self.rules)
        return 0