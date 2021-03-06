from beancount.core.number import D
from beancount.ingest import importer
from beancount.core import account
from beancount.core import amount
from beancount.core import flags
from beancount.core import data
from beancount.core.position import Cost

from dateutil.parser import parse

from titlecase import titlecase

import csv
import os
import re

class AmexImporter(importer.ImporterProtocol):
    def __init__(self, account):
        self.account = account

    def identify(self, f):
        if not re.match('amex.*\.csv', os.path.basename(f.name)):
            return False

        return True

    def extract(self, f):
        entries = []

        with open(f.name) as f:
            for index, row in enumerate(csv.DictReader(f)):
                trans_date = parse(row['Date']).date()
                trans_desc = titlecase(row['Description'])
                trans_amt  = row['Amount']

                if trans_desc == "Online Payment - Thank You":
                    # Record these at the bank level
                    continue

                if trans_desc == "Payment Received - Thank You":
                    # Record these at the bank level
                    continue

                meta = data.new_metadata(f.name, index)

                txn = data.Transaction(
                    meta=meta,
                    date=trans_date,
                    flag=flags.FLAG_OKAY,
                    payee=trans_desc,
                    narration="",
                    tags=set(),
                    links=set(),
                    postings=[],
                )

                txn.postings.append(
                    data.Posting(
                        self.account,
                        amount.Amount(-1*D(trans_amt), 'USD'),
                        None, None, None, None
                    )
                )

                entries.append(txn)

        return entries
