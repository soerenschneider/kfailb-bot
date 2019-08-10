
class IncidentFormatter:
    @staticmethod
    def format_incident(incident):
        """
        Formats a incident as a message that is presented to the user.
        :param incident: The incident
        :return: A formatted message containing information about the incident.
        """
        if not incident:
            return ""

        ret = ""
        ret += "*" + incident['what'] + "* \n"

        if 'direction' in incident:
            ret += "_" + incident['direction'] + "_ \n"

        if 'stations' in incident:
            for station in incident['stations']:
                if 'station' in station and 'time' in station:
                    ret += f"{station['station']}:{station['time']}" + "\n"
                else:
                    ret += f"{station}" + "\n"
        ret += "\n"

        return ret
