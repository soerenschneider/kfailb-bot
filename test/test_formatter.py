from unittest import TestCase

from kfailbot import incidentformatter
from kfailbot import Incident


class TestFormatter(TestCase):

    def test_format_incident_2(self):
        direction = 'Klettenbergpark -> Herler Str.'
        what = 'Folgende Fahrt entfällt'
        line = 18
        stations = list()
        incident = Incident(line=line, what=what, stations=stations)
        print(incident)
        stations.append('Klettenbergpark (12:26h)')
        stations.append('Barbarossaplatz (12:38h)')
        stations.append('Neumarkt (12:41h)')
        stations.append('Dom/Hbf (12:44h)')
        stations.append('Ebertplatz (12:47h)')
        stations.append('Reichenspergerpl. (12:48h)')
        stations.append('Wiener Platz (12:55h)')
        stations.append('Herler Str. (12:58h)')


        output = incidentformatter.IncidentFormatter.format_incident(incident)
        expected = """*Folgende Fahrt entfällt* 
Klettenbergpark (12:26h)
Barbarossaplatz (12:38h)
Neumarkt (12:41h)
Dom/Hbf (12:44h)
Ebertplatz (12:47h)
Reichenspergerpl. (12:48h)
Wiener Platz (12:55h)
Herler Str. (12:58h)
"""
        assert expected.strip() == output.strip()

    def test_format_incident_3(self):
        direction = ''
        line = 155
        stations = list()

        what = 'Baumaßnahme im Bereich der (H) Am Porzenacker * Dadurch fahren die Busse nicht den' \
                           ' üblichen Linienweg * Die (H) Am Porzenacker ist in beiden Richtungen vor bzw. hinter' \
                           ' die die Einmündung Am Porzenacker und die (H) Klosterhof in Richtung (H) Mülheim' \
                           ' Berliner Str. bzw. (H) Ostheim ist auf die Prämonstatenerstr. hinter die Einmündung' \
                           ' Holzweg verlegt * Die (H) Hildegundweg kann in diesem Zeitraum nicht bedient werden *'
        incident = Incident(line=line, what=what, stations=stations)

        output = incidentformatter.IncidentFormatter.format_incident(incident)
        print(output)
