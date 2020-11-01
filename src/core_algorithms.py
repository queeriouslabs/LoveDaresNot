import secrets


RAND_POSITIVE_WIDTH = 1000000


def random_snot_dare_number():
    return secrets.randbelow(2 * RAND_POSITIVE_WIDTH + 1) - RAND_POSITIVE_WIDTH


class UnanimousSnotDareRound(object):

    def __init__(self, snot_dare, own_ip, all_consensor_ips):
        self.snot_dare = snot_dare
        self.own_ip = own_ip
        self.other_consensor_ips = [
            ip for ip in all_consensor_ips if ip != own_ip]
        self.responses = {}
        self.own_response = None
        self.has_been_announced = False
        self.cached_announcement = None
        self.announcements = {}

    def add_own_response(self, response):
        if self.own_response is not None:
            return self.own_response

        self.own_response = response
        others_number_count = len(self.other_consensor_ips)

        while True:
            others_numbers = [random_snot_dare_number()
                              for i in range(others_number_count)]

            total_others = sum(others_numbers)

            if abs(total_others) <= RAND_POSITIVE_WIDTH:
                yes_response = -total_others + abs(random_snot_dare_number())
                no_response = -total_others

                if response == 'yes':
                    own_number = yes_response
                    plausible_deniability_number = no_response
                elif response == 'no':
                    own_number = no_response
                    plausible_deniability_number = yes_response

                break

        self.own_response = {
            'response': response,
            'own_number': own_number,
            'plausible_deniability_number': plausible_deniability_number,
            'others_numbers': dict(zip(self.other_consensor_ips, others_numbers))
        }

        return self.own_response

    def add_response(self, consensor_ip, number):
        if consensor_ip not in self.responses:
            self.responses[consensor_ip] = number

    def announcement(self):
        if self.cached_announcement is not None:
            return self.cached_announcement

        if self.own_response is None:
            return None

        all_found = True
        for ip in self.other_consensor_ips:
            if ip not in self.responses:
                all_found = False
                break

        if not all_found:
            return None
        else:
            self.cached_announcement = self.own_response['own_number'] + \
                sum(self.responses.values())

            return self.cached_announcement

    def add_announcement(self, sender_ip, announced_number):
        self.announcements[sender_ip] = announced_number

    def result(self):
        if self.cached_announcement is None:
            return 'unknown'

        all_found = True
        total = self.cached_announcement
        for ip in self.other_consensor_ips:
            if ip not in self.announcements:
                all_found = False
                break
            total += self.announcements[ip]

        if all_found:
            if total == 0:
                return 'no'
            else:
                return 'yes'
        else:
            return 'unknown'
