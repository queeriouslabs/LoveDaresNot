import json
import re
import requests
import threading
import time
import uuid

import core_algorithms


def is_ip_address(str):
    return re.match('^\d+\.\d+\.\d+\.\d+:\d+$', str) is not None


INTERNAL_need_to_propose_snot_dare_prefix = 'INTERNAL: need to propose snot dare? '
INTERNAL_is_this_bit_one_prefix = 'INTERNAL: is this bit one? '


def is_need_to_propose_snot_dare(snot_dare):
    return snot_dare[0:len(INTERNAL_need_to_propose_snot_dare_prefix)] == INTERNAL_need_to_propose_snot_dare_prefix


def propose_snot_dare_id(snot_dare):
    return snot_dare[len(INTERNAL_need_to_propose_snot_dare_prefix) + 1:]


def is_external_snot_dare(snot_dare):
    return snot_dare[0:10] == 'EXTERNAL: '


def external_snot_dare_content(snot_dare):
    return snot_dare[10:]


def message_to_bit_array(mstr):
    max_chars = 128
    max_bits = max_chars * 8

    if mstr is None:
        return max_bits * [0]
    else:
        bits = []
        for c in mstr[0:max_chars]:
            bits += char_to_bit_array(c)
        pad_width = max_bits - len(bits)
        return bits + pad_width * [0]


def char_to_bit_array(c):
    c = ord(c)
    bits = []
    for shift in range(7, -1, -1):
        if c & (1 << shift) == 0:
            bits.append(0)
        else:
            bits.append(1)
    return bits


class SnotDareManager(object):

    def __init__(self, ip_address, role):
        self.mode = 'setup'
        self.role = role
        self.ip_address = ip_address
        self.consensors = []
        self.incoming_messages = []
        self.time_asleep = 0
        self.unanimous_rounds = {}
        self.watched_unanimous_rounds = []
        self.send_queue = []
        self.send_state = None

    def setup_consensors(self, consensors):
        print('Setting up consensors: ' + repr(consensors))
        if not all([is_ip_address(c) for c in consensors]):
            return False
        elif self.mode == 'setup':
            self.consensors = list(set(consensors + [self.ip_address]))
            self.start()
            print('All consensors: ' + repr(self.consensors))

            if self.role == 'manager':
                for c in self.consensors:
                    if c != self.ip_address:
                        print('Sending consensor info to ' + c)
                        print('Consensors: ' + repr(self.consensors))
                        url = 'http://' + c
                        requests.post(
                            url, data={'consensors': self.consensors})

            return True

    def start(self):
        self.mode = 'consensing'

        def daemon():
            while True:
                self.main_loop()

        thread = threading.Thread(target=daemon)
        thread.daemon = True
        thread.start()

    def main_loop(self):
        # handle commitments and announcements
        for snot_dare, round in self.unanimous_rounds.items():
            commitment = round.announcement_commitment()
            if not round.has_been_committed and commitment is not None:
                self.commit_round(round)

            announcement = round.announcement()
            if not round.has_been_announced and announcement is not None:
                self.announce_round(round)

        # handle messages
        while len(self.incoming_messages) > 0:
            msg = self.incoming_messages[0]
            self.incoming_messages = self.incoming_messages[1:]
            self.handle_message(msg)

        if self.role == 'manager':
            if self.time_asleep >= 5:
                print()
                print('=== summaries ===')
                for summary in self.snot_dare_summaries(debug=True):
                    print(summary)

                print()
                print()

                # send a call for snot dares
                new_call_id = uuid.uuid4().hex
                snot_dare = INTERNAL_need_to_propose_snot_dare_prefix + new_call_id

                for ip in self.consensors:
                    url = 'http://' + ip + '/api/messages'
                    msg = {
                        'type': 'single_round_unanimous',
                        'snot_dare': snot_dare,
                        'consensor_ips': self.consensors
                    }
                    requests.post(url, json=json.dumps(msg))

                self.time_asleep = 0

        self.time_asleep += 0.001
        time.sleep(0.001)

    def handle_message(self, msg):
        print()
        print()
        print('---------------- handling message ----------------')
        print()
        print('Message: ' + repr(msg))
        if msg['type'] == 'single_round_unanimous':
            snot_dare = msg['snot_dare']

            if snot_dare not in self.unanimous_rounds:
                self.unanimous_rounds[snot_dare] = core_algorithms.UnanimousSnotDareRound(
                    snot_dare, self.ip_address, msg['consensor_ips'])
            round = self.unanimous_rounds[snot_dare]

            if 'sender_ip' in msg:
                if 'response' in msg:
                    round.add_response(msg['sender_ip'], msg['response'])
                elif 'commitment' in msg:
                    self.add_commitment(msg)
                elif 'announced_number' in msg:
                    self.add_announcement(msg)

            if is_need_to_propose_snot_dare(snot_dare):
                if snot_dare not in self.watched_unanimous_rounds:
                    self.watched_unanimous_rounds.append(snot_dare)

                print()
                print('Need To Propose Snot Dare: ' + snot_dare)
                if round.own_response is None:
                    print('This snot dare has not yet been answered.')
                    self.do_need_to_propose_snot_dare(snot_dare)

    def do_need_to_propose_snot_dare(self, snot_dare):
        if len(self.send_queue) > 0:
            response = 'yes'
        else:
            response = 'no'

        round = self.unanimous_rounds[snot_dare]
        resp = round.add_own_response(response)
        self.send_round_response(snot_dare, resp)

    def send_round_response(self, snot_dare, response):
        print('Sending round response')
        print('  Snot Dare: ' + snot_dare)
        print('  Response: ' + repr(response))

        for ip, number in response['others_numbers'].items():
            message = json.dumps({
                'type': 'single_round_unanimous',
                'consensor_ips': [self.ip_address] + self.unanimous_rounds[snot_dare].other_consensor_ips,
                'sender_ip': self.ip_address,
                'snot_dare': snot_dare,
                'response': number
            })
            requests.post('http://' + ip + '/api/messages',
                          json=message)

    def commit_round(self, round):
        round.has_been_committed = True
        print('Committing round: ' + round.snot_dare)
        print('Commitment: ' + round.announcement_commitment())
        message = json.dumps({
            'type': 'single_round_unanimous',
            'consensor_ips': [self.ip_address] + round.other_consensor_ips,
            'sender_ip': self.ip_address,
            'snot_dare': round.snot_dare,
            'commitment': round.announcement_commitment()
        })
        for ip in round.other_consensor_ips:

            requests.post('http://' + ip + '/api/messages',
                          json=message)

    def announce_round(self, round):
        round.has_been_announced = True
        print('Announcing round: ' + round.snot_dare)
        message = json.dumps({
            'type': 'single_round_unanimous',
            'consensor_ips': [self.ip_address] + round.other_consensor_ips,
            'sender_ip': self.ip_address,
            'snot_dare': round.snot_dare,
            'announced_number': round.announcement()
        })
        for ip in round.other_consensor_ips:

            requests.post('http://' + ip + '/api/messages',
                          json=message)

    def add_commitment(self, commitment):
        print()
        print()
        print('---------------- received commitment ----------------')
        print()
        print('Commitment: ' + repr(commitment))
        if commitment['snot_dare'] in self.unanimous_rounds:
            round = self.unanimous_rounds[commitment['snot_dare']]
            round.add_announcement_commitment(
                commitment['sender_ip'], commitment['commitment'])

    def add_announcement(self, announcement):
        print()
        print()
        print('---------------- received announcement ----------------')
        print()
        print('Announcement: ' + repr(announcement))
        if announcement['snot_dare'] in self.unanimous_rounds:
            round = self.unanimous_rounds[announcement['snot_dare']]
            old_result = round.result()
            round.add_announcement(
                announcement['sender_ip'], announcement['announced_number'])
            new_result = round.result()
            if old_result != new_result:
                print()
                print('ROUND RESULT: ' + round.snot_dare)
                print(new_result)
                if round.snot_dare in self.watched_unanimous_rounds:
                    self.watched_round_completed(round.snot_dare)

    def watched_round_completed(self, snot_dare):
        round = self.unanimous_rounds[snot_dare]
        if is_need_to_propose_snot_dare(snot_dare):
            self.watched_unanimous_rounds.remove(snot_dare)
            if round.result() == 'yes':
                self.begin_propose_snot_dare_process(
                    propose_snot_dare_id(snot_dare))

    def begin_propose_snot_dare_process(self, call_round_id):
        print('!!!!! BEGINNING SNOT DARE PROPOSAL PROCESS')
        exit()

        if len(self.send_queue) > 0:
            snot_dare = self.send_queue[0]

            print('SENDING SNOT DARE: ' + snot_dare)

    def send_new_snot_dare(self, snot_dare):
        self.send_queue += [snot_dare]

    def snot_dare_summaries(self, debug=False):
        summaries = []

        for snot_dare, round in self.unanimous_rounds.items():
            if debug or is_external_snot_dare(snot_dare):
                summaries.append({
                    'other_consensor_ips': round.other_consensor_ips,
                    'snot_dare': snot_dare,
                    'own_response': round.own_response,
                    'responses': round.responses,
                    'result': round.result()
                })

        return summaries
