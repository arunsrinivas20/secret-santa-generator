import random
import functools
import json
import sys
import smtplib, ssl, email
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

EMAIL_SENDER = None
PASSWORD = None
EMAIL_PORT = 465  

class Graph:
    def __init__(self, people_info):
        self.vertices = set(people_info.keys())
        self.edges = {}

        for p1 in people_info:
            self.edges[p1] = set()
            for p2 in people_info:
                if p1 != p2:
                    self.edges[p1].add(p2)

            self.edges[p1] = self.edges[p1].difference(set(people_info[p1]['restrictions']))
        
    def remove_edge(self, assignment):
        for person in self.vertices:
            if assignment in self.edges[person]:
                self.edges[person].remove(assignment)

    def get_person_with_fewest_edges(self):
        num_edges = float('inf')
        res = None

        for person in self.vertices:
            plen = len(self.edges[person]) 
            if plen < num_edges:
                res = person
                num_edges = plen

        return res

    def assign_secret_santa(self):
        assignments = {}

        while self.vertices:
            person = self.get_person_with_fewest_edges()

            s = self.edges[person]
            while (len(s) > 1):
                s.remove(random.sample(s, 1)[0])

            target = s.pop()
            assignments[person] = target

            self.vertices.remove(person)
            self.remove_edge(target)

        return assignments

def compare_names(a, b):
    if len(a) > len(b):
        return a
    else:
        return b

def process_people_json(json_file):
    res = {}

    with open(json_file, 'r') as f:
        info = json.load(f)
        for person in info:
            p_info = info[person]
            res[person] = p_info

    return res

def print_format_assignments(assignments):
    longest_len = len(functools.reduce(lambda a, b: compare_names(a, b), list(people_info.keys())))

    print('PERSON               ASSIGNMENT')
    print('-' * longest_len, '        ', '-' * longest_len)
    for (a, b) in assignments.items():
        spaces = ' ' * (longest_len - len(a) + 1)
        print(f'{a}{spaces}=======> {b}')

def wishlist_str(wishlist):
    res = ''

    for (index, item) in enumerate(wishlist):
        res += f'\n\t\t{index + 1}. {item}'

    return res

def email_assignments(person_info, assignments):
    for (person, assignment) in assignments.items():
        email = person_info[person]['email']
        wishlist = person_info[assignment]['wishlist']

        body = f"""
Dear {person},

This email contains your Secret Santa assignment and their wishlist. Good luck and happy holidays!

Assignment: {assignment}
Wishlist (IN ORDER): {wishlist_str(wishlist)}

Thanks,
Your Friendly Email Service
"""

        print(body)
        # message = MIMEMultipart()
        # message["To"] = email
        # message["Subject"] = f'Ski Trip 3K20 - Secret Santa Assignment'

        # message.attach(MIMEText(body, "plain"))

        # text = message.as_string()

        # context = ssl.create_default_context()

        # with smtplib.SMTP_SSL("smtp.gmail.com", EMAIL_PORT, context=context) as server:
        #     server.login(EMAIL_SENDER, PASSWORD)
        #     server.sendmail(EMAIL_SENDER, email, text)

if __name__ == "__main__":
    if (len(sys.argv) == 1 or len(sys.argv) > 4):
        raise Exception("Invalid command. Arguments are incorrect.")
    else:
        if '.json' not in sys.argv[1]:
            raise Exception("JSON file was not provided.")

        EMAIL_SENDER = sys.argv[2]
        PASSWORD = sys.argv[3]

    # A Dictionary mapping a string to dictionaries
    #   - Each dictionary contains the string's email, wishlist, and restrictions
    people_info = process_people_json(sys.argv[1])

    g = Graph(people_info)

    secret_santa_assignments = g.assign_secret_santa()

    #print_format_assignments(secret_santa_assignments)

    email_assignments(people_info, secret_santa_assignments)