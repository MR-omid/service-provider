import datetime
import io
import json
from . import patterns
import re
from copy import deepcopy


class Parser(object):
    """   parse whois data and return json   """

    def __init__(self):
        # Why do the below? The below is meant to handle with an edge case (issue #2) where a partial match followed
        # by a failure, for a regex containing the \s*.+ pattern, would send the regex module on a wild goose hunt for
        # matching positions. The workaround is to use \S.* instead of .+, but in the interest of keeping the regexes
        # consistent and compact, it's more practical to do this (predictable) conversion on runtime.
        # FIXME: This breaks on NIC contact regex for nic.at. Why?
        self.registrant_regexes = [self.__preprocess_regex(regex) for regex in patterns.registrant_regexes]
        self.tech_contact_regexes = [self.__preprocess_regex(regex) for regex in patterns.tech_contact_regexes]
        self.admin_contact_regexes = [self.__preprocess_regex(regex) for regex in patterns.admin_contact_regexes]
        self.billing_contact_regexes = [self.__preprocess_regex(regex) for regex in
                                        patterns.billing_contact_regexes]
        self.grammar = deepcopy(patterns.grammar)
        self.grammar["_data"]["id"] = self.__precompile_regexes(patterns.grammar["_data"]["id"], re.IGNORECASE)
        self.grammar["_data"]["status"] = self.__precompile_regexes(patterns.grammar["_data"]["status"],
                                                                    re.IGNORECASE)
        self.grammar["_data"]["creation_date"] = self.__precompile_regexes(
            patterns.grammar["_data"]["creation_date"], re.IGNORECASE)
        self.grammar["_data"]["expiration_date"] = self.__precompile_regexes(
            patterns.grammar["_data"]["expiration_date"], re.IGNORECASE)
        self.grammar["_data"]["updated_date"] = self.__precompile_regexes(patterns.grammar["_data"]["updated_date"],
                                                                          re.IGNORECASE)
        self.grammar["_data"]["registrar"] = self.__precompile_regexes(patterns.grammar["_data"]["registrar"],
                                                                       re.IGNORECASE)
        self.grammar["_data"]["whois_server"] = self.__precompile_regexes(patterns.grammar["_data"]["whois_server"],
                                                                          re.IGNORECASE)
        self.grammar["_data"]["domain_name"] = self.__precompile_regexes(patterns.grammar["_data"]["domain_name"],
                                                                         re.IGNORECASE)
        self.grammar["_data"]["nameservers"] = self.__precompile_regexes(patterns.grammar["_data"]["nameservers"],
                                                                         re.IGNORECASE)
        self.grammar["_data"]["emails"] = self.__precompile_regexes(patterns.grammar["_data"]["emails"],
                                                                    re.IGNORECASE)

        self.grammar["_dateformats"] = self.__precompile_regexes(patterns.grammar["_dateformats"], re.IGNORECASE)

        self.registrant_regexes = self.__precompile_regexes(self.registrant_regexes)
        self.tech_contact_regexes = self.__precompile_regexes(self.tech_contact_regexes)
        self.billing_contact_regexes = self.__precompile_regexes(self.billing_contact_regexes)
        self.admin_contact_regexes = self.__precompile_regexes(self.admin_contact_regexes)
        self.nic_contact_regexes = self.__precompile_regexes(patterns.nic_contact_regexes)
        self.organization_regexes = self.__precompile_regexes(patterns.organization_regexes, re.IGNORECASE)
        self.nic_contact_references = deepcopy(patterns.nic_contact_references)
        self.nic_contact_references["registrant"] = self.__precompile_regexes(
            patterns.nic_contact_references["registrant"])
        self.nic_contact_references["tech"] = self.__precompile_regexes(patterns.nic_contact_references["tech"])
        self.nic_contact_references["admin"] = self.__precompile_regexes(patterns.nic_contact_references["admin"])
        self.nic_contact_references["billing"] = self.__precompile_regexes(
            patterns.nic_contact_references["billing"])

    def __preprocess_regex(self, regex):
        """

        :param regex:determine one regex
        :return: prosessed form of input regex
        """
        # Fix for #2; prevents a ridiculous amount of varying size permutations.
        regex = re.sub(r"\\s\*\(\?P<([^>]+)>\.\+\)", r"\s*(?P<\1>\S.*)", regex)
        # Experimental fix for #18; removes unnecessary variable-size whitespace
        # matching, since we're stripping results anyway.
        regex = re.sub(r"\[ \]\*\(\?P<([^>]+)>\.\*\)", r"(?P<\1>.*)", regex)
        return regex

    def __parse_raw_whois(self, raw_data):
        # FIXME: set percentage of founded data with parse and add to result if parse is not complete!

        data = {}
        raw_data = [segment.replace("\r", "") for segment in raw_data]

        for segment in raw_data:
            for rule_key, rule_regexes in self.grammar['_data'].items():
                if not (rule_key in data):
                    for line in segment.splitlines():
                        for regex in rule_regexes:
                            result = re.search(regex, line)
                            if result is not None:
                                val = result.group("val").strip()
                                if val != "":
                                    try:
                                        data[rule_key].append(val)
                                    except KeyError as e:
                                        # if self.debug:
                                        #     custom_logger.log_says(custom_logger.ERR, "error:" + str(e))
                                        data[rule_key] = [val]

            # Whois.com is a bit special... Fabulous.com also seems to use this format. As do some others.
            match = re.search("^\s?Name\s?[Ss]ervers:?\s*\n((?:\s*.+\n)+?\s?)\n", segment, re.MULTILINE)
            if match is not None:
                chunk = match.group(1)
                for match in re.findall("[ ]*(.+)\n", chunk):
                    if match.strip() != "":
                        if not re.match("^[a-zA-Z]+:", match):
                            if "nameservers" in data:
                                data["nameservers"].append(match.strip())
                            else:
                                data["nameservers"] = [match.strip()]

            # Nominet also needs some special attention
            match = re.search("    Registrar:\n        (.+)\n", segment)
            if match is not None:
                data["registrar"] = [match.group(1).strip()]
            match = re.search("    Registration status:\n        (.+)\n", segment)
            if match is not None:
                data["status"] = [match.group(1).strip()]
            match = re.search("    Name servers:\n([\s\S]*?\n)\n", segment)
            if match is not None:
                chunk = match.group(1)
                for match in re.findall("        (.+)\n", chunk):
                    match = match.split()[0]
                    if "nameservers" in data:
                        data["nameservers"].append(match.strip())
                    else:
                        data["nameservers"] = [match.strip()]
            # janet (.ac.uk) is kinda like Nominet, but also kinda not
            match = re.search("Registered By:\n\t(.+)\n", segment)
            if match is not None:
                data["registrar"] = [match.group(1).strip()]
            match = re.search("Entry created:\n\t(.+)\n", segment)
            if match is not None:
                data["creation_date"] = [match.group(1).strip()]
            match = re.search("Renewal date:\n\t(.+)\n", segment)
            if match is not None:
                data["expiration_date"] = [match.group(1).strip()]
            match = re.search("Entry updated:\n\t(.+)\n", segment)
            if match is not None:
                data["updated_date"] = [match.group(1).strip()]
            match = re.search("Servers:([\s\S]*?\n)\n", segment)
            if match is not None:
                chunk = match.group(1)
                for match in re.findall("\t(.+)\n", chunk):
                    match = match.split()[0]
                    if "nameservers" in data:
                        data["nameservers"].append(match.strip())
                    else:
                        data["nameservers"] = [match.strip()]
            # .am plays the same game
            match = re.search("   DNS servers:([\s\S]*?\n)\n", segment)
            if match is not None:
                chunk = match.group(1)
                for match in re.findall("      (.+)\n", chunk):
                    match = match.split()[0]
                    if "nameservers" in data:
                        data["nameservers"].append(match.strip())
                    else:
                        data["nameservers"] = [match.strip()]
            # SIDN isn't very standard either. And EURid uses a similar format.
            match = re.search("Registrar:\n\s+(?:Name:\s*)?(\S.*)", segment)
            if match is not None:
                try:
                    data["registrar"].insert(0, match.group(1).strip())
                except KeyError as e:
                    if self.debug:
                        pass
                    data["registrar"] = match.group(1).strip()
            match = re.search("(?:Domain nameservers|Name servers):([\s\S]*?\n)\n", segment)
            if match is not None:
                chunk = match.group(1)
                for match in re.findall("\s+?(.+)\n", chunk):
                    match = match.split()[0]
                    # Prevent nameserver aliases from being picked up.
                    if not match.startswith("[") and not match.endswith("]"):
                        if "nameservers" in data:
                            data["nameservers"].append(match.strip())
                        else:
                            data["nameservers"] = [match.strip()]
            # The .ie WHOIS server puts ambiguous status information in an unhelpful order
            match = re.search('ren-status:\s*(.+)', segment)
            if match is not None:
                if "status" in data:
                    data["status"].insert(0, match.group(1).strip())
                else:
                    data['status'] = match.group(1).strip()

            # nic.it gives us the registrar in a multi-line format...
            match = re.search('Registrar\n  Organization:     (.+)\n', segment)
            if match is not None:
                data["registrar"] = [match.group(1).strip()]
            # HKDNR (.hk) provides a weird nameserver format with too much whitespace
            match = re.search("Name Servers Information:\n\n([\s\S]*?\n)\n", segment)
            if match is not None:
                chunk = match.group(1)
                for match in re.findall("(.+)\n", chunk):
                    match = match.split()[0]
                    if "nameservers" in data:
                        data["nameservers"].append(match.strip())
                    else:
                        data["nameservers"] = [match.strip()]
            # ... and again for TWNIC.
            match = re.search("   Domain servers in listed order:\n([\s\S]*?\n)\n", segment)
            if match is not None:
                chunk = match.group(1)
                for match in re.findall("      (.+)\n", chunk):
                    match = match.split()[0]
                    try:
                        data["nameservers"].append(match.strip())
                    except KeyError as e:
                        if self.debug:
                            pass
                        data["nameservers"] = [match.strip()]

        data["contacts"] = self.__parse_registrants(raw_data)

        # Parse dates
        if 'expiration_date' in data:
            data['expiration_date'] = self.__remove_duplicates(data['expiration_date'])
            data['expiration_date'] = self.__parse_dates(data['expiration_date'])

        if 'creation_date' in data:
            data['creation_date'] = self.__remove_duplicates(data['creation_date'])
            data['creation_date'] = self.__parse_dates(data['creation_date'])

        if 'updated_date' in data:
            data['updated_date'] = self.__remove_duplicates(data['updated_date'])
            data['updated_date'] = self.__parse_dates(data['updated_date'])

        if 'nameservers' in data:
            data['nameservers'] = self.__remove_suffixes(data['nameservers'])
            data['nameservers'] = self.__remove_duplicates([ns.rstrip(".") for ns in data['nameservers']])

        if 'domain_name' in data:
            data['domain_name'] = self.__remove_suffixes(data['domain_name'])
            data['domain_name'] = self.__remove_duplicates([ns.rstrip(".") for ns in data['domain_name']])

        if 'emails' in data:
            data['emails'] = self.__remove_duplicates(data['emails'])

        if 'registrar' in data:
            data['registrar'] = self.__remove_duplicates(data['registrar'])

        # Remove e-mail addresses if they are already listed for any of the contacts
        known_emails = []
        for contact in ("registrant", "tech", "admin", "billing"):
            if data["contacts"][contact] is not None:
                try:
                    known_emails.append(data["contacts"][contact]["email"])
                except KeyError as e:
                    pass  # No e-mail recorded for this contact...
        try:
            data['emails'] = [email for email in data["emails"] if email not in known_emails]
        except KeyError as e:
            pass

        for key in list(data.keys()):
            if data[key] is None or len(data[key]) == 0:
                del data[key]

        data["raw"] = raw_data
        return self.__validate_data(data)

    def __parse_dates(self, dates):
        """

        :param dates:determine a list of dates
        :return: a list contains parsed form of dates
        """
        parsed_dates = []

        for date in dates:
            for rule in self.grammar['_dateformats']:
                result = re.match(rule, date)

                if result is not None:
                    try:
                        # These are always numeric. If they fail, there is no valid date present.
                        year = int(result.group("year"))
                        day = int(result.group("day"))

                        # Detect and correct shorthand year notation
                        if year < 60:
                            year += 2000
                        elif year < 100:
                            year += 1900

                        # This will require some more guesswork - some WHOIS servers present the name of the month
                        try:
                            month = int(result.group("month"))
                        except ValueError as e:
                            # Apparently not a number. Look up the corresponding number.
                            try:
                                month = self.grammar['_months'][result.group("month").lower()]
                            except KeyError as e:
                                # Unknown month name, default to 0
                                month = 0

                        try:
                            hour = int(result.group("hour"))
                        except IndexError as e:
                            hour = 0
                        except TypeError as e:
                            hour = 0

                        try:
                            minute = int(result.group("minute"))
                        except IndexError as e:
                            minute = 0
                        except TypeError as e:
                            minute = 0

                        try:
                            second = int(result.group("second"))
                        except IndexError as e:
                            second = 0
                        except TypeError as e:
                            second = 0

                        break
                    except ValueError as e:
                        # Something went horribly wrong, maybe there is no valid date present?
                        year = 0
                        month = 0
                        day = 0
                        hour = 0
                        minute = 0
                        second = 0

            try:
                if year > 0:
                    try:
                        parsed_dates.append(datetime.datetime(year, month, day, hour, minute, second))
                    except ValueError as e:

                        parsed_dates.append(datetime.datetime(year, day, month, hour, minute, second))
            except UnboundLocalError as e:

                pass

        if len(parsed_dates) > 0:
            return parsed_dates
        else:
            return None

    def __remove_duplicates(self, data):
        """

        :param data: list of dates
        :return: list without duplicated date
        """
        cleaned_list = []

        for entry in data:
            if entry not in cleaned_list:
                cleaned_list.append(entry)

        return cleaned_list

    def __remove_suffixes(self, data):
        # Removes everything before and after the first non-whitespace continuous string.
        # Used to get rid of IP suffixes for nameservers.
        """

        :param data:list of dates
        :return: a clean list of dates without suffixes
        """
        cleaned_list = []

        for entry in data:
            cleaned_list.append(re.search("([^\s]+)\s*[\s]*", entry).group(1).lstrip())

        return cleaned_list

    def __parse_registrants(self, data):
        """

        :param data:list of dates
        :return: a dictionary contains registrant
        """
        registrant = None
        tech_contact = None
        billing_contact = None
        admin_contact = None

        for segment in data:
            for regex in self.registrant_regexes:
                match = re.search(regex, segment)
                if match is not None:
                    registrant = match.groupdict()
                    break

        for segment in data:
            for regex in self.tech_contact_regexes:
                match = re.search(regex, segment)
                if match is not None:
                    tech_contact = match.groupdict()
                    break

        for segment in data:
            for regex in self.admin_contact_regexes:
                match = re.search(regex, segment)
                if match is not None:
                    admin_contact = match.groupdict()
                    break

        for segment in data:
            for regex in self.billing_contact_regexes:
                match = re.search(regex, segment)
                if match is not None:
                    billing_contact = match.groupdict()
                    break

        # Find NIC handle contact definitions
        handle_contacts = self.__parse_nic_contact(data)

        # Find NIC handle references and process them
        missing_handle_contacts = []
        for category in self.nic_contact_references:
            for regex in self.nic_contact_references[category]:
                for segment in data:
                    match = re.search(regex, segment)
                    if match is not None:
                        data_reference = match.groupdict()
                        if data_reference["handle"] == "-" or re.match("https?:\/\/",
                                                                       data_reference["handle"]) is not None:
                            pass  # Reference was either blank or a URL; the latter is to deal with false positives for nic.ru
                        else:
                            found = False
                            for contact in handle_contacts:
                                if contact["handle"] == data_reference["handle"]:
                                    found = True
                                    data_reference.update(contact)

                            if category == "registrant":
                                registrant = data_reference
                            elif category == "tech":
                                tech_contact = data_reference
                            elif category == "billing":
                                billing_contact = data_reference
                            elif category == "admin":
                                admin_contact = data_reference

        # Post-processing
        for obj in (registrant, tech_contact, billing_contact, admin_contact):
            if obj is not None:
                for key in list(obj.keys()):
                    if obj[key] is None or obj[key].strip() == "":  # Just chomp all surrounding whitespace
                        del obj[key]
                    else:
                        obj[key] = obj[key].strip()
                if "phone_ext" in obj:
                    if "phone" in obj:
                        obj["phone"] += " ext. %s" % obj["phone_ext"]
                        del obj["phone_ext"]
                if "street1" in obj:
                    street_items = []
                    i = 1
                    while True:
                        try:
                            street_items.append(obj["street%d" % i])
                            del obj["street%d" % i]
                        except KeyError as e:
                            # if self.debug:
                            #     custom_logger.log_says(custom_logger.ERR, "error :" + str(e))
                            break
                        i += 1
                    obj["street"] = "\n".join(street_items)
                if "organization1" in obj:  # This is to deal with eg. HKDNR, who allow organization names in
                    # multiple languages.
                    organization_items = []
                    i = 1
                    while True:
                        if "organization%d" % i.strip() in obj and obj["organization%d" % i].strip() != "":
                            organization_items.append(obj["organization%d" % i])
                            del obj["organization%d" % i]
                        else:
                            break
                        i += 1
                    obj["organization"] = "\n".join(organization_items)
                if 'changedate' in obj:
                    obj['changedate'] = self.__parse_dates([obj['changedate']])[0]
                if 'creationdate' in obj:
                    obj['creationdate'] = self.__parse_dates([obj['creationdate']])[0]
                if 'street' in obj and "\n" in obj["street"] and 'postalcode' not in obj:
                    # Deal with certain mad WHOIS servers that don't properly delimit address data... (yes, AFNIC,
                    # looking at you)
                    lines = [x.strip() for x in obj["street"].splitlines()]
                    if " " in lines[-1]:
                        postal_code, city = lines[-1].split(" ", 1)
                        if "." not in lines[-1] and re.match("[0-9]", postal_code) and len(postal_code) >= 3:
                            obj["postalcode"] = postal_code
                            obj["city"] = city
                            obj["street"] = "\n".join(lines[:-1])
                if 'firstname' in obj or 'lastname' in obj:
                    elements = []
                    if 'firstname' in obj:
                        elements.append(obj["firstname"])
                    if 'lastname' in obj:
                        elements.append(obj["lastname"])
                    obj["name"] = " ".join(elements)
                if 'country' in obj and 'city' in obj and (
                        re.match("^R\.?O\.?C\.?$", obj["country"], re.IGNORECASE) or obj[
                    "country"].lower() == "republic of china") and obj["city"].lower() == "taiwan":
                    # There's an edge case where some registrants append ", Republic of China" after "Taiwan",
                    # and this is mis-parsed as Taiwan being the city. This is meant to correct that.
                    obj["country"] = "%s, %s" % (obj["city"], obj["country"])
                    lines = [x.strip() for x in obj["street"].splitlines()]
                    obj["city"] = lines[-1]
                    obj["street"] = "\n".join(lines[:-1])

        return {
            "registrant": registrant,
            "tech": tech_contact,
            "admin": admin_contact,
            "billing": billing_contact,
        }

    def __parse_nic_contact(self, data):
        """

        :param data: list of data
        :return: list of useful contacts
        """
        handle_contacts = []
        for regex in self.nic_contact_regexes:
            for segment in data:
                matches = re.finditer(regex, segment)
                for match in matches:
                    handle_contacts.append(match.groupdict())

        return handle_contacts

    def __precompile_regexes(self, source, flags=0):
        """

        :param source:
        :param flags:
        :return:
        """
        return [re.compile(regex, flags) for regex in source]

    def __parse_zone(self, data):
        """

        :param data: whois raw data
        :return: a dictionary contains zone data
        """
        result = {}
        regx = "(.+).\s+\d+\s+IN\s+(\w+)\s+(.+)"
        n = 1
        for i in data:
            i = io.StringIO(str(i))
            for b in i:
                if len(b.strip()) > 10:
                    r = re.findall(regx, b, re.MULTILINE | re.IGNORECASE)
                    try:
                        record_type = r[0][1]
                        record_value = r[0][2]
                        try:
                            if record_type == "NS":
                                record_type = record_type.replace("NS", "NS%d" % n)
                                n += 1
                            result.update({record_type: record_value})
                        except TypeError:
                            raise TypeError
                    except IndexError:
                        raise IndexError
        return {"zone": result}

    def __json_fallback(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        else:
            return obj

    def parse_data(self, data, as_json=False, zone=None):
        """
        parse whois result and extract information from it .
        :param data: whois raw data
        :param as_json: set return format as json if True
        :param zone: zone data
        :return: whois information
        """
        parsed = self.__parse_raw_whois(data)
        if zone is not None:
            parsed.update(self.__parse_zone(zone))
        if as_json:
            return json.dumps(parsed, default=self.__json_fallback)
        return parsed

    def get_emails(self, data, as_json=False):
        """
          extract all emails from raw string
        :param data: determine raw input data
        :param as_json: a boolean that determine we want json result or not
        :return: a dictionary contains email data with it' properties
        """
        parsed_data = self.__parse_raw_whois(data)
        result = []
        known_values = []

        # parsing email  from contact block
        for contact, info in parsed_data['contacts'].items():
            is_valid = {}
            owner = {'owner': '', 'type': 11}
            organization = {'organization': '', 'type': 11}
            local_address = {'local_address': '', 'type': 5}
            domain_name = {'domain_name': '', 'type': 12}
            # ToDo: check pause or cancel flag here
            if info is not None:
                properties_list = []
                special_properties_list = []
                d = {'type': 2, 'data': '', 'properties': {}, 'special_properties': {}, 'is_valid': False, 'ref': {}}
                for name, value in info.items():
                    if name == "email":
                        if value in known_values:
                            break
                        d['data'] = value
                        known_values.append(value)
                        try:
                            domain_name['domain_name'] = value.split('@')[1]
                            local_address['local_address'] = value.split('@')[0]
                        except:
                            domain_name['domain_name'] = ''
                            local_address['local_address'] = value
                        d['is_valid'] = parsed_data['valid']
                        is_valid = {'isvalid': parsed_data['valid'], 'type': 0}

                    if name == "organization":
                        organization['organization'] = value
                    if name == "name":
                        owner['owner'] = value
                # prevent from create result if phone number of contact is not available
                if d['data'] == '':
                    continue
                d.update({'ref': {'task': 'whois', 'whois_for': '', 'whois_from': '', 'label': ''}})
                d['ref']['label'] = "%s_name" % contact
                if 'domain_name' in parsed_data and len(parsed_data['domain_name']) > 0:
                    d['ref']['whois_for'] = parsed_data['domain_name'][0]
                if 'whois_server' in parsed_data:
                    if type(parsed_data['whois_server']) is list:
                        d['ref']['whois_from'] = parsed_data['whois_server'][-1]
                    else:
                        d['ref']['whois_from'] = parsed_data['whois_server']
                properties_list.append(owner)
                properties_list.append(organization)
                properties_list.append(local_address)
                properties_list.append(domain_name)
                d['properties'] = properties_list
                special_properties_list.append(is_valid)
                d['special_properties'] = special_properties_list
                result.append(d)
        # parsing email  from email block
        if 'emails' in parsed_data:
            for email in parsed_data['emails']:
                is_valid = {}
                owner = {'owner': '', 'type': 11}
                organization = {'organization': '', 'type': 11}
                local_address = {'local_address': '', 'type': 5}
                domain_name = {'domain_name': '', 'type': 12}
                if email in known_values:
                    continue
                d = {'type': 2, 'data': email, 'properties': {}, 'special_properties': {}, 'is_valid': False, 'ref': {}}
                properties_list = []
                special_properties_list = []
                known_values.append(email)
                try:
                    local_address['local_address'] = email.split('@')[0]
                    domain_name['domain_name'] = email.split('@')[1]
                except:
                    local_address['local_address'] = email
                    domain_name['domain_name'] = ''
                d['is_valid'] = parsed_data['valid']
                is_valid = {'isvalid': parsed_data['valid'], 'type': 0}
                organization['organization'] = ""
                owner['owner'] = ""
                d.update({'ref': {'task': 'whois', 'whois_for': '', 'whois_from': ''}})
                if 'domain_name' in parsed_data and len(parsed_data['domain_name']) > 0:
                    d['ref']['whois_for'] = parsed_data['domain_name'][0]
                if 'whois_server' in parsed_data:
                    if type(parsed_data['whois_server']) is list:
                        d['ref']['whois_from'] = parsed_data['whois_server'][-1]
                    else:
                        d['ref']['whois_from'] = parsed_data['whois_server']
                properties_list.append(owner)
                properties_list.append(organization)
                properties_list.append(local_address)
                properties_list.append(domain_name)
                d['properties'] = properties_list
                special_properties_list.append(is_valid)
                d['special_properties'] = special_properties_list
                result.append(d)
        # parsing email from all block, where an email detect vy regex matching
        match = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', str(re.sub(r"(\\n|\\r|\\t)", " ", str(parsed_data['raw']))))
        for email in match:
            is_valid = {}
            owner = {'owner': '', 'type': 11}
            organization = {'organization': '', 'type': 11}
            local_address = {'local_address': '', 'type': 5}
            domain_name = {'domain_name': '', 'type': 12}
            if email not in known_values:
                d = {'type': 2, 'data': email, 'properties': {}, 'special_properties': {}, 'is_valid': False, 'ref': {}}
                properties_list = []
                special_properties_list = []
                known_values.append(email)
                try:
                    local_address['local_address'] = email.split('@')[0]
                    domain_name['domain_name'] = email.split('@')[1]
                except:
                    local_address['local_address'] = email
                    domain_name['domain_name'] = ''
                d['is_valid'] = parsed_data['valid']
                is_valid = {'isvalid': parsed_data['valid'], 'type': 0}
                organization['organization'] = ""
                owner['owner'] = ""
                d.update({'ref': {'task': 'whois', 'whois_for': '', 'whois_from': ''}})
                if 'domain_name' in parsed_data and len(parsed_data['domain_name']) > 0:
                    d['ref']['whois_for'] = parsed_data['domain_name'][0]
                if 'whois_server' in parsed_data:
                    if type(parsed_data['whois_server']) is list:
                        d['ref']['whois_from'] = parsed_data['whois_server'][-1]
                    else:
                        d['ref']['whois_from'] = parsed_data['whois_server']
                properties_list.append(owner)
                properties_list.append(organization)
                properties_list.append(local_address)
                properties_list.append(domain_name)
                d['properties'] = properties_list
                special_properties_list.append(is_valid)
                d['special_properties'] = special_properties_list
                result.append(d)

        result = self.__remove_duplicates(result)
        if as_json:
            return json.dumps(result, default=self.__json_fallback)
        return result

    # parsing phones
    def get_phones(self, data, as_json=False):
        """
         extract all phone numbers from raw string
        :param data: determine raw input data
        :param as_json: a boolean that determine we want json result or not
        :return:  a dictionary contains phone data with it' properties
        """
        parsed_data = self.__parse_raw_whois(data)
        result = []
        known_values = []

        # parsing phone number from contact block
        for contact, info in parsed_data['contacts'].items():
            if info is not None:
                d = {'type': 4, 'data': '', 'properties': {}, 'special_properties': {}, 'ref': {}}
                # properties dictionary
                owener = {'type': 11, 'owner': ''}
                location = {'type': 11, 'location': ''}
                properties_list = []
                special_properties_list = []
                d.update({'ref': {'task': 'whois', 'whois_for': '', 'whois_from': ''}})
                if 'domain_name' in parsed_data and len(parsed_data['domain_name']) > 0:
                    d['ref']['whois_for'] = parsed_data['domain_name'][0]
                if 'whois_server' in parsed_data:
                    if type(parsed_data['whois_server']) is list:
                        d['ref']['whois_from'] = parsed_data['whois_server'][-1]
                    else:
                        d['ref']['whois_from'] = parsed_data['whois_server']
                for name, value in info.items():
                    if name == "phone":
                        if value in known_values:
                            break
                        d['data'] = value
                        known_values.append(value)
                    if name == "name":
                        owener['owner'] = value
                        properties_list.append(owener)

                    if name == "city":
                        location['location'] = value
                        properties_list.append(location)
                # prevent from create result if phone number of contact is not available
                if d['data'] == '':
                    continue
                special_properties_list.append({'phone_type': '', 'type': 0})
                special_properties_list.append({'country_code': '', 'type': 0})
                special_properties_list.append({'operator': '', 'type': 0})
                special_properties_list.append({'is_valid': '', 'type': 0})
                d['special_properties'] = special_properties_list
                d['properties'] = properties_list
                result.append(d)

        # parsing phone from all block, where an email detect by regex matching
        match = re.findall(r'(?:(\+)?(\d{1,3})?(-)?(.)?\(?(\d{3})\)?[\s -\.]?)?(\d{3})[\s -\.]?(\d{4,5})[\s -\.]?',
                           str(parsed_data['raw']))
        for phone in match:
            # properties dictionary
            phone = ''.join(phone)
            if phone not in known_values:
                properties_list = []
                special_properties_list = []
                d = {'type': 4, 'data': phone, 'properties': {}, 'special_properties': {}, 'ref': {}}
                known_values.append(phone)
                d.update({'ref': {'task': 'whois', 'whois_for': '', 'whois_from': ''}})
                if 'domain_name' in parsed_data and len(parsed_data['domain_name']) > 0:
                    d['ref']['whois_for'] = parsed_data['domain_name'][0]
                if 'whois_server' in parsed_data:
                    if type(parsed_data['whois_server']) is list:
                        d['ref']['whois_from'] = parsed_data['whois_server'][-1]
                    else:
                        d['ref']['whois_from'] = parsed_data['whois_server']
                special_properties_list.append({'phone_type': '', 'type': 0})
                special_properties_list.append({'country_code': '', 'type': 0})
                special_properties_list.append({'operator': '', 'type': 0})
                special_properties_list.append({'is_valid': '', 'type': 0})
                properties_list.append({'owner': '', 'type': 11})
                properties_list.append({'location': '', 'type': 11})
                d['special_properties'] = special_properties_list
                d['properties'] = properties_list
                result.append(d)

        result = self.__remove_duplicates(result)
        if as_json:
            return json.dumps(result, default=self.__json_fallback)
        return result

    # def get_domains(self, data, as_json=False):
    #     """
    #     extract all domain names from raw string
    #     :param data: determine raw input data
    #     :param as_json: a boolean that determine we want json result or not
    #     :return: a dictionary contains domain data with it' properties
    #     """
    #     parsed_data = self.__parse_raw_whois(data)
    #     result = []
    #     known_values = []
    #     d = {'type': 12, 'data': '', 'properties': {}}
    #     if 'domain_name' in parsed_data and len(parsed_data['domain_name']) > 0:
    #         d['data'] = parsed_data['domain_name'][0]
    #         known_values.append(parsed_data['domain_name'][0])
    #     d['properties'].update({'ref': {'task': 'whois', 'whois_for': '', 'whois_from': ''}})
    #     if 'domain_name' in parsed_data and len(parsed_data['domain_name']) > 0:
    #         d['properties']['ref']['whois_for'] = parsed_data['domain_name'][0]
    #     if 'whois_server' in parsed_data:
    #         d['properties']['ref']['whois_from'] = parsed_data['whois_server']
    #     if 'nameservers' in parsed_data:
    #         d['properties']['name_servers'] = parsed_data['nameservers']
    #     if 'expiration_date' in parsed_data:
    #         d['properties']['expiration_date'] = parsed_data['expiration_date']
    #     if 'updated_date' in parsed_data:
    #         d['properties']['updated_date'] = parsed_data['updated_date']
    #     if 'creation_date' in parsed_data:
    #         d['properties']['creation_date'] = parsed_data['creation_date']
    #     if 'registrar' in parsed_data:
    #         d['properties']['registrar'] = parsed_data['registrar']
    #     d['properties']['contacts'] = parsed_data['contacts']
    #     d['properties'].update({'valid': parsed_data['valid'], "should_be_fixed": False})
    #     result.append(d)
    #     match = re.findall(r'(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,6}',
    #                        str(re.sub(r"(\\n|\\r|\\t)", " ", str(parsed_data['raw']))))
    #     for domain in match:
    #         domain = domain.replace('www.', '')
    #         if domain not in known_values:
    #             d = {'type': 12, 'data': domain, 'properties': {}}
    #             known_values.append(domain)
    #             d['properties']['name'] = ''
    #             d['properties'].update({'ref': {'task': 'whois', 'whois_for': '', 'whois_from': ''}})
    #             if 'domain_name' in parsed_data and len(parsed_data['domain_name']) > 0:
    #                 d['properties']['ref']['whois_for'] = parsed_data['domain_name'][0]
    #             if 'whois_server' in parsed_data:
    #                 d['properties']['ref']['whois_from'] = parsed_data['whois_server']
    #             d['properties'].update({'valid': parsed_data['valid'], "should_be_fixed": False})
    #             result.append(d)
    #     result = self.__remove_duplicates(result)
    #     if as_json:
    #         return json.dumps(result, default=self.__json_fallback)
    #     return result

    def get_main_srtucture(self, data, has_dns, as_json=False):
        """
         extract all contacts from whois parsed data
        :param data: determine raw input data
        :param as_json: a boolean that determine we want json result or not
        :return: a dictionary contains main structure data with it' properties
        """
        parsed_data = self.__parse_raw_whois(data)

        result = {"properties": {}, "results": {'data': {}}, "special_properties": {}}
        special_properties_list = []
        properties_list = []

        # creating ref block in result block
        result['results'].update({'ref': {'task': 'whois', 'whois_for': '', 'whois_from': ''}})
        result['results'].update({'type': 0})
        if 'domain_name' in parsed_data and len(parsed_data['domain_name']) > 0:
            result['results']['ref']['whois_for'] = parsed_data['domain_name'][0]

        if 'whois_server' in parsed_data:
            if parsed_data['whois_server'] is list:
                result['results']['ref']['whois_from'] = parsed_data['whois_server'][-1]
            else:
                result['results']['ref']['whois_from'] = parsed_data['whois_server']

        # creating special_properties in main structure
        special_properties_list.append({'valid': parsed_data['valid'], 'type': 0})
        special_properties_list.append({'should_be_fixed': False, 'type': 0})
        special_properties_list.append({'has_dns': has_dns, 'type': 0})

        # creating properties of main structure
        if 'contacts' in parsed_data:
            try:
                if 'registrant' in parsed_data['contacts']:
                    if 'name' in parsed_data['contacts']['registrant']:
                        properties_list.append(
                            {'registrant_name': parsed_data['contacts']['registrant']['name'], 'type': 11})
            except Exception:
                properties_list.append(
                    {'registrant_name': '', 'type': 11})
            try:
                if 'admin' in parsed_data['contacts']:
                    if 'name' in parsed_data['contacts']['admin']:
                        properties_list.append({'admin_name': parsed_data['contacts']['admin']['name'], 'type': 11})
            except Exception:
                properties_list.append({'admin_name': '', 'type': 11})
            try:
                if 'tech' in parsed_data['contacts']:
                    if 'name' in parsed_data['contacts']['tech']:
                        properties_list.append({'tech_name': parsed_data['contacts']['tech']['name'], 'type': 11})
            except Exception:
                properties_list.append({'tech_name': '', 'type': 11})

        if 'nameservers' in parsed_data and len(parsed_data['nameservers']) > 0:
            known_dns = []
            for i in parsed_data['nameservers']:
                if i in known_dns:
                    continue
                else:

                    properties_list.append({'dns': i, 'type': 3})
                    known_dns.append(i)
        else:
            properties_list.append({'dns': '', 'type': 3})

        if 'registration_date' in parsed_data and len(parsed_data['registration_date']) > 0:
            known_reg = []
            for i in parsed_data['registration_date']:
                if i in known_reg:
                    continue
                else:
                    known_reg.append(i)
                    properties_list.append({'registration_date': i, 'type': 0})
        else:
            properties_list.append({'registration_date': '', 'type': 0})

        if 'expiration_date' in parsed_data and len(parsed_data['expiration_date']) > 0:
            known_date = []
            for i in parsed_data['expiration_date']:
                if i in known_date:
                    continue
                else:
                    properties_list.append({'expiration_date': i, 'type': 0})
                    known_date.append(i)

        else:
            properties_list.append({'expiration_date': '', 'type': 0})

        result['special_properties'] = special_properties_list
        result['properties'] = properties_list

        # creating data of registrant, admin, tech info for result
        for contact, info in parsed_data['contacts'].items():
            if contact == 'billing':
                continue
            d = {contact: {}}
            d[contact] = {'name': '', 'phone': '', 'fax': '', 'country': '', 'city': '', 'street': '', 'email': ''}
            if info is not None:
                for name, value in info.items():
                    if name == "name":
                        d[contact]['name'] = value
                    if name == "phone":
                        d[contact]['phone'] = value
                    if name == "fax":
                        d[contact]['fax'] = value
                    if name == "country":
                        d[contact]['country'] = value
                    if name == "city":
                        d[contact]['city'] = value
                    if name == "street":
                        d[contact]['street'] = value
                    if name == "postalcode":
                        d[contact]['postalcode'] = value
                    if name == "email":
                        d[contact]['email'] = value
                    if name == "organization":
                        d[contact]['organization'] = value
            d[contact].update({'type': 'whois_contact_name'})
            result['results']['data'].update(d)

        if as_json:
            return json.dumps(result, default=self.__json_fallback)
        return result

    def get_names(self, data):

        parsed_data = self.__parse_raw_whois(data)
        known_values = []
        result = []
        # properties dictionary
        fax = {'fax': '', 'type': 4}
        phone = {'phone': '', 'type': 4}
        country = {'country': '', 'type': 11}
        street = {'street': '', 'type': 8}
        city = {'city': '', 'type': 11}
        email = {'email': '', 'type': 2}
        # get name from contacts
        for contact, info in parsed_data['contacts'].items():
            if info is not None:
                d = {'type': 11, 'data': '', 'properties': {}, 'special_properties': {}, 'ref': {}}
                properties_list = []
                special_properties_list = []
                d.update({'ref': {'task': 'whois', 'whois_for': '', 'whois_from': ''}})
                if 'domain_name' in parsed_data and len(parsed_data['domain_name']) > 0:
                    d['ref']['whois_for'] = parsed_data['domain_name'][0]
                if 'whois_server' in parsed_data:
                    if type(parsed_data['whois_server']) is list:
                        d['ref']['whois_from'] = parsed_data['whois_server'][-1]
                    else:
                        d['ref']['whois_from'] = parsed_data['whois_server']
                for name, value in info.items():
                    if name == "name":
                        # prevent from duplicate name
                        if value in known_values:
                            break
                        d['data'] = value
                    if name == 'city':
                        city['city'] = value
                    if name == 'street':
                        street['street'] = value
                    if name == 'country':
                        country['country'] = value
                    if name == 'phone':
                        phone['phone'] = value
                    if name == 'fax':
                        fax['fax'] = value
                    if name == 'email':
                        email['email'] = value
                # if name is null, discard other info
                if d['data'] == '':
                    continue
                # saving name special properties
                special_properties_list.append({'is_username': False, 'type': 0})
                special_properties_list.append({'is_domain_name': False, 'type': 0})
                special_properties_list.append({'is_public_name': False, 'type': 0})
                special_properties_list.append({'is_account_name': False, 'type': 0})
                d['special_properties'] = special_properties_list
                properties_list.append(fax)
                properties_list.append(phone)
                properties_list.append(country)
                properties_list.append(street)
                properties_list.append(city)
                properties_list.append(email)
                d['properties'] = properties_list
                result.append(d)
        result = self.__remove_duplicates(result)
        return result

    def __validate_data(self, data):
        """
         validate whois data, data should contain least two contact info
        :param data: determine dictionary of data for validation
        :return: dictionary contains validated data
        """
        count = 0
        for contact, info in data['contacts'].items():
            if info is not None:
                count += 1
        if count > 0:
            return dict(data, **{'valid': True})
        return dict(data, **{'valid': False})

    @staticmethod
    def invalid_result(has_dns=False):
        """

        :param has_dns:a boolean for dns parameter
        :return: customized dictionary for special state and functionality
        """
        return [{'type': 0,
                 'properties': {'valid': False, 'has_dns': has_dns,
                                'ref': {'whois_for': '', 'task': 'whois', 'whois_from': ''},
                                'should_be_fixed': False}, 'data': {}}]
