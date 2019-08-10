from unittest import TestCase

from kfailbot import incidentformatter


class TestFormatter(TestCase):

    def test_format_incident(self):
        incident = dict()
        incident['direction'] = ''
        incident['line'] = 1
        incident['station'] = list()
        incident['what'] = 'Streckensanierung zwischen (H) Refrath und (H) Bensberg * Die Bahnen fahren bis 12.08.' \
                           ' ca. 03:00h nur zwischen (H) Weiden West und (H) Refrath * Zwischen (H) Refrath und (H)' \
                           ' Bensberg sind Ersatzbusse der Linie 101 für Sie eingesetzt *'

        print(incidentformatter.IncidentFormatter.format_incident(incident))

    def test_format_incident_2(self):
        incident = dict()
        incident['direction'] = 'Klettenbergpark -> Herler Str.'
        incident['line'] = 18
        stations = list()
        incident['stations'] = stations
        stations.append('Klettenbergpark (12:26h)')
        stations.append('Barbarossaplatz (12:38h)')
        stations.append('Neumarkt (12:41h)')
        stations.append('Dom/Hbf (12:44h)')
        stations.append('Ebertplatz (12:47h)')
        stations.append('Reichenspergerpl. (12:48h)')
        stations.append('Wiener Platz (12:55h)')
        stations.append('Herler Str. (12:58h)')

        incident['what'] = 'Folgende Fahrt entfällt'

        output = incidentformatter.IncidentFormatter.format_incident(incident)
        expected = """*Folgende Fahrt entfällt* 
_Klettenbergpark -> Herler Str._ 
Klettenbergpark (12:26h)
Barbarossaplatz (12:38h)
Neumarkt (12:41h)
Dom/Hbf (12:44h)
Ebertplatz (12:47h)
Reichenspergerpl. (12:48h)
Wiener Platz (12:55h)
Herler Str. (12:58h)

"""
        assert expected == output

    def test_format_incident_3(self):
        incident = dict()
        incident['direction'] = ''
        incident['line'] = 155
        incident['station'] = list()

        incident['what'] = 'Baumaßnahme im Bereich der (H) Am Porzenacker * Dadurch fahren die Busse nicht den' \
                           ' üblichen Linienweg * Die (H) Am Porzenacker ist in beiden Richtungen vor bzw. hinter' \
                           ' die die Einmündung Am Porzenacker und die (H) Klosterhof in Richtung (H) Mülheim' \
                           ' Berliner Str. bzw. (H) Ostheim ist auf die Prämonstatenerstr. hinter die Einmündung' \
                           ' Holzweg verlegt * Die (H) Hildegundweg kann in diesem Zeitraum nicht bedient werden *'

        output = incidentformatter.IncidentFormatter.format_incident(incident)
        print(output)
