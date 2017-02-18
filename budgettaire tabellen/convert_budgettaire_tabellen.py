#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv, codecs, cStringIO
import json
import os
import re
from collections import defaultdict

# Script that does more clean up on begrotingsstaten_first_step.csv and
# writes the output to another .csv called
# 'begrotingsstaten.csv' and the directory
# 'begrotingsstaten_json' which contains a .json file holding the values
# in a nested way for each combination of year,
# uitgaven (U)/verplichtingen (V)/ontvangsten (O) and type of budget
# (i.e., ontwerpbegroting/vastgestelde_begroting/
# eerste_suppletoire_begroting/tweede_suppletoire_begroting/realisatie).
# The .json files are hierarchically structured in the format used for
# hierarchical visualisations by D3.js
# (https://github.com/d3/d3-hierarchy/blob/master/README.md#hierarchy).

# Script to convert budgettaire tabellen data to a new file containing no totals

# Classes to read and write UTF-8 .csv's
class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")

class UnicodeReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]

    def __iter__(self):
        return self

class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


# Mapping of hoofdstuk indicator to the name of the hoofdstuk
mapping = {
    "A": "Infrastructuurfonds",
    "B": "Gemeentefonds",
    "C": "Provinciefonds",
    "F": "Diergezondheidsfonds",
    "H": "BES-fonds",
    "I": "De Koning",
    "IIA": "De Staten Generaal",
    "IIB": "Overige Hoge Colleges van Staat",
    "III": "Algemene Zaken",
    "IV": "Koninkrijksrelaties",
    "IXA": "Nationale Schuld",
    "IXB": u"Financiën",
    "J": "Deltafonds",
    "V": "Buitenlandse Zaken",
    "VII": "Binnenlandse Zaken en Koninkrijksrelaties",
    "VIII": "Onderwijs, Cultuur en Wetenschap",
    "VI": "Veiligheid en Justitie",
    "X": "Defensie",
    "XIII": "Economische Zaken",
    "XII": "Infrastructuur en Milieu",
    "XVII": "Buitenlandse Handel & Ontwikkelingssamenwerking",
    "XVIII": "Wonen en Rijksdienst",
    "XVI": "Volksgezondheid, Welzijn en Sport",
    "XV": "Sociale Zaken en Werkgelegenheid"
}

# Set up the datastructure for the .json output files
tree = lambda: defaultdict(tree)

def print_existing(item, uvo, hoofdstuk, artikel, artikelonderdeel, subartikelonderdeel, uitsplitsing, omschrijving, new_line):
    print 'uvo: ' + uvo
    print 'h: ' + hoofdstuk
    print 'a: ' + artikel
    print 'ad: ' + artikelonderdeel
    print 'sad: ' + subartikelonderdeel
    print 'u: ' + uitsplitsing
    print 'o: ' + omschrijving
    print 'Already filled item!! %s' % (item)
    print 'Overwriting with: %s\n' % (new_line)

def store_json_data(json_data, uvo, hoofdstuk, artikel, new_line):
    artikelonderdeel = new_line[15].strip()
    subartikelonderdeel = new_line[16].strip()
    uitsplitsing = new_line[17].strip()
    omschrijving = new_line[18].strip()
    if omschrijving:
        try:
            if json_data[uvo][hoofdstuk][artikel][artikelonderdeel][subartikelonderdeel][uitsplitsing][omschrijving]:
                print_existing(json_data[uvo][hoofdstuk][artikel][artikelonderdeel][subartikelonderdeel][uitsplitsing][omschrijving], uvo, hoofdstuk, artikel, artikelonderdeel, subartikelonderdeel, uitsplitsing, omschrijving, new_line)
                return
        except TypeError:
            print_existing(json_data[uvo][hoofdstuk][artikel][artikelonderdeel][subartikelonderdeel], uvo, hoofdstuk, artikel, artikelonderdeel, subartikelonderdeel, uitsplitsing, omschrijving, new_line)
            return
        json_data[uvo][hoofdstuk][artikel][artikelonderdeel][subartikelonderdeel][uitsplitsing][omschrijving] = new_line[21]
    elif uitsplitsing:
        try:
            if json_data[uvo][hoofdstuk][artikel][artikelonderdeel][subartikelonderdeel][uitsplitsing]:
                print_existing(json_data[uvo][hoofdstuk][artikel][artikelonderdeel][subartikelonderdeel][uitsplitsing], uvo, hoofdstuk, artikel, artikelonderdeel, subartikelonderdeel, uitsplitsing, omschrijving, new_line)
                return
        except TypeError:
            print_existing(json_data[uvo][hoofdstuk][artikel][artikelonderdeel], uvo, hoofdstuk, artikel, artikelonderdeel, subartikelonderdeel, uitsplitsing, omschrijving, new_line)
            return
        json_data[uvo][hoofdstuk][artikel][artikelonderdeel][subartikelonderdeel][uitsplitsing] = new_line[21]
    elif subartikelonderdeel:
        try:
            if json_data[uvo][hoofdstuk][artikel][artikelonderdeel][subartikelonderdeel]:
                print_existing(json_data[uvo][hoofdstuk][artikel][artikelonderdeel][subartikelonderdeel], uvo, hoofdstuk, artikel, artikelonderdeel, subartikelonderdeel, uitsplitsing, omschrijving, new_line)
                return
        except TypeError:
            print_existing(json_data[uvo][hoofdstuk][artikel][artikelonderdeel][subartikelonderdeel], uvo, hoofdstuk, artikel, artikelonderdeel, subartikelonderdeel, uitsplitsing, omschrijving, new_line)
            return
        json_data[uvo][hoofdstuk][artikel][artikelonderdeel][subartikelonderdeel] = new_line[21]
    elif artikelonderdeel:
        try:
            if json_data[uvo][hoofdstuk][artikel][artikelonderdeel]:
                print_existing(json_data[uvo][hoofdstuk][artikel][artikelonderdeel], uvo, hoofdstuk, artikel, artikelonderdeel, subartikelonderdeel, uitsplitsing, omschrijving, new_line)
                return
        except TypeError:
            print_existing(json_data[uvo][hoofdstuk][artikel][artikelonderdeel], uvo, hoofdstuk, artikel, artikelonderdeel, subartikelonderdeel, uitsplitsing, omschrijving, new_line)
            return
        json_data[uvo][hoofdstuk][artikel][artikelonderdeel] = new_line[21]
    else:
        try:
            if json_data[uvo][hoofdstuk][artikel]:
                print_existing(json_data[uvo][hoofdstuk][artikel], uvo, hoofdstuk, artikel, artikelonderdeel, subartikelonderdeel, uitsplitsing, omschrijving, new_line)
                return
        except TypeError:
            print_existing(json_data[uvo][hoofdstuk][artikel], uvo, hoofdstuk, artikel, artikelonderdeel, subartikelonderdeel, uitsplitsing, omschrijving, new_line)
            return
        json_data[uvo][hoofdstuk][artikel] = new_line[21]

def clean(year):
    # This dictionary will be used to keep track of the largest total
    # value found for a certain artikel. If this artikel doesn't have
    # any detailed values then use this total value as its most detailed
    # value.
    dict_data = tree()
    # This dictionary will be used to store the data in a hierarchical
    # way in order to be exported to json
    json_data = tree()

    # All rows are doubled in 2016, so don't process a hoofdstuk if
    # we've seen it already
    seen = {}
    
    # Open the .csv files to read from and write to
    with open('budgettaire_tabellen_owb_%s_origineel.csv' % (year)) as IN, \
        open('budgettaire_tabellen_owb_%s.csv' % (year), 'w') as OUT:
        budget_data = UnicodeReader(IN)
        writer = UnicodeWriter(OUT)
        # Retrieve the first line containing the column names
        column_names = budget_data.next()
        # Write the first line containing the column names to the .csv
        # file
        writer.writerow(column_names)

        seen_last_row = ''

        # Process each line of the input data
        line_count = 1
        for line in budget_data:
            line_count += 1
            # Store any changes to the line in new_line
            new_line = line

            # Logic to tell if we've already seen a whole block of one
            # hoofdstuk in 2016 in order to skip the second block with
            # the same values
            if line[0] == '2016' and line[1] in seen:
                continue
            elif line[0] == '2016' and line[1] not in seen:
                if seen_last_row != line[1] and seen_last_row:
                    seen[seen_last_row] = True
            seen_last_row = line[1]

            # This line contains years as values which is incorrect so
            # skip it in 2017
            if line_count == 1409 and line[0] == '2017':
                continue

            artikel = new_line[6]

            # The following two lines contain
            # 'V/U/O (Verplichtingen/Uitgaven/Ontvangsten)' instead of
            # 'V' as value in 2017
            if (line_count == 2313 or line_count == 2332) and line[0] == '2017':
                new_line[12] = 'V'
            # Sometimes lowercase values are used, 'u'/'v'/'o', convert them to upper case
            uvo = new_line[12].strip().upper()

            # The input .csv files use just 'III' for three different
            # begrotingen, so correct these to the codes that are used
            # on rijksbegroting.nl, e.g.
            # http://rijksbegroting.nl/2017/voorbereiding/begroting,kst225610.html
            if new_line[3] == 'Algemene Zaken':
                new_line[1] = 'IIIA'
            elif new_line[3] == 'Kabinet van de Koning':
                new_line[1] = 'IIIB'
            elif new_line[3] == 'Commissie van Toezicht betreffende de Inlichtingen- en Veiligheidsdienst':
                new_line[1] = 'IIIC'
            hoofdstuk = new_line[1]

            # In 2017, the last 7/8 columns of lines 899-936 have
            # shifted one column to the right
            if line_count in range(899, 937) and line[0] == '2017':
                if new_line[19].strip():
                    new_line[18] = new_line[19]
                new_line[19:] = new_line[20:]

            # Column T has a 'o' instead of a 0 in 2017
            if line_count == 2419 and line[0] == '2017':
                new_line[19] = '0'

            # Change line[3] to 'Overige Hoge Colleges van Staat en
            # Kabinetten van de Gouverneurs' instead of
            # 'Staten Generaal' in 2016 and 2017 for hoofdstuk IIB
            if new_line[1] == 'IIB' and (new_line[0] == '2016' or new_line[0] == '2017') and new_line[3] == 'Staten Generaal':
                new_line[3] = 'Overige Hoge Colleges van Staat en Kabinetten van de Gouverneurs'

            # In 2017, the 'Deltafonds' hoofdstuk value is 'A' instead
            # of 'J' in 2017
            if new_line[3] == 'Deltafonds' and new_line[0] == '2017':
                hoofdstuk = 'J'

            # Remove lines containing either 'pm' ('pro memorie', i.e., the value is not (yet) known) or '%' or if it doesn't contain a number
            if not new_line[21] or 'pm' in new_line[21] or '%' in new_line[21] or not re.search(r'\d', new_line[21].strip()):
                continue

            # Remove the comma thousand separator 
            val = new_line[21].replace(',', '')

            # 2015 uses badly formatted floats, so round those values
            if '.' in val:
                val = round(float(val))
            val = int(val)

            new_line[21] = unicode(val)

            # Don't output lines with a 'J' in column N as these are
            # (sub)totals which we don't need as we can calculate them
            # using the most detailed values. We do store the maximum
            # total values found as some artikelen don't have detailed
            # values so this total value will be the most detailed
            # value.
            if new_line[13] == 'J':
                if 'max_val' in dict_data[hoofdstuk][artikel][uvo]:
                    if val > dict_data[hoofdstuk][artikel][uvo]['max_val']:
                        dict_data[hoofdstuk][artikel][uvo]['max_val'] = val
                        dict_data[hoofdstuk][artikel][uvo]['max_val_line'] = new_line
                else:
                    dict_data[hoofdstuk][artikel][uvo]['max_val'] = val
                    dict_data[hoofdstuk][artikel][uvo]['max_val_line'] = new_line
            # If column N has the value 'N', then this line contains a
            # detailed value so write it to the output .csv file and
            # also set the 'has_detailed_values' flag which shows that
            # this artikel has detailed values
            else:
                writer.writerow(new_line)

                # Store data for JSON export
                store_json_data(json_data, uvo, hoofdstuk, artikel, new_line)

                if 'has_detailed_values' not in dict_data[hoofdstuk][artikel][uvo]:
                    dict_data[hoofdstuk][artikel][uvo]['has_detailed_values'] = True
        # Some artikelen don't have detailed values and only a total
        # value. If this is the case then write this line to the .csv
        # file as well, because it is the most detailed value.
        for hoofdstuk, hoofdstuk_values in dict_data.iteritems():
            for artikel, artikel_values in hoofdstuk_values.iteritems():
                for uvo, uvo_values in artikel_values.iteritems():
                    if not 'has_detailed_values' in uvo_values:
                        writer.writerow(uvo_values['max_val_line'])
                        # Store data for JSON export
                        store_json_data(json_data, uvo, hoofdstuk, artikel, uvo_values['max_val_line'])
    return json_data

def recursively_extract(parent_item):
    if type(parent_item) == unicode:
        return u'found_leaf'
    item_list = []
    for item, item_value in parent_item.iteritems():
        child_item_return = recursively_extract(item_value)
        if child_item_return == u'found_leaf':
            item_list.append(
                {
                    "name": item,
                    "value": item_value
                }
            )
        if type(child_item_return) == list:
            item_list.append(
                {
                    "name": item,
                    "children": child_item_return
                }
            )
    return item_list


# Loop over all years
years = ['2015', '2016', '2017']
for year in years:
    json_data = clean(year)

    ## Save hierarchical JSON data
    # Directory name to save the .json files in
    dirname = 'budgettaire_tabellen_json'
    # Create the directory if it does not exist
    if not os.path.exists(dirname):
        os.mkdir(dirname)
    # Loop over all hierarchies in the dictionary
    for uvo, uvo_values in json_data.iteritems():
        # Open a .json file for this combination of year, uvo and
        # budget_type (we currently only take ontwerpbegroting value
        # 't'/column N) to write to
        filename = '%s-%s-%s' % (year, uvo, 'ontwerpbegroting')
        with open('%s/%s.json' % (dirname, filename), 'w') as OUT:
            hoofdstuk_list = recursively_extract(uvo_values)
            out_data = { 
                "name": filename,
                "children": hoofdstuk_list
            }
            json.dump(out_data, OUT, indent=4)

            #hoofdstuk_list = []
            #for hoofdstuk, hoofdstuk_values in uvo_values.iteritems():
            #    artikel_list = []
            #    for artikel, artikel_values in hoofdstuk_values.iteritems():
            #        artikelonderdeel_list = []
            #        for artikelonderdeel, artikelonderdeel_values in artikel_values.iteritems():
            #            subartikelonderdeel_list = []
            #            for subartikelonderdeel, subartikelonderdeel_values in artikelonderdeel_values.iteritems():
            #                uitsplitsing_list = []
            #                for uitsplitsing, uitsplitsing_values in subartikelonderdeel_values.iteritems():
            #                    if type(uitsplitsing_values) == str:
            #                        uitsplitsing_list.append(
            #                            {
            #                                "name": uitsplitsing,
            #                                "size": uitsplitsing_values
            #                            }
            #                        )
            #                    omschrijving_list = []
            #                    for omschrijving, value in uitsplitsing_values.iteritems():
            #                        omschrijving_list.append(
            #                            {
            #                                "name": omschrijving,
            #                                "size": value
            #                            }
            #                        )
            #                    uitsplitsing_list.append(
            #                        {
            #                            "name": uitsplitsing,
            #                            "children": omschrijving_list
            #                        }
            #                    )
            #                subartikelonderdeel_list.append(
            #                    {
            #                        "name": subartikelonderdeel,
            #                        "children": uitsplitsing_list
            #                    }
            #                )
            #            artikelonderdeel_list.append(
            #                {
            #                    "name": artikelonderdeel,
            #                    "children": subartikelonderdeel_list
            #                }
            #            )
            #        artikel_list.append(
            #            {
            #                "name": artikel,
            #                "children": artikelonderdeel_list
            #            }
            #        )
            #    hoofdstuk_list.append(
            #        {
            #            "name": hoofdstuk,
            #            "children": artikel_list
            #        }
            #    )
            #out_data = { 
            #    "name": filename,
            #    "children": hoofdstuk_list
            #}

            #json.dump(out_data, OUT, indent=4)