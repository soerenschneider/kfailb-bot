
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
        ret += "*" + incident.what + "* \n"

        if incident.direction:
            ret += "_" + incident.direction + "_ \n"

        if incident.stations:
            for station in incident.stations:
                    ret += f"{station}" + "\n"

        return ret
