"""
Tests unitaires — Module humidex
==================================
Valide le calcul de l'indice Humidex et la correspondance
classes/seuils selon Masterton & Richardson (1979).
"""

import pytest

from biosense360.humidex import calculer_humidex, classe_depuis_humidex


# ---------------------------------------------------------------------------
# calculer_humidex
# ---------------------------------------------------------------------------


class TestCalculerHumidex:
    """Tests du calcul de l'indice Humidex."""

    def test_conditions_normales(self):
        """Humidex doit être proche de la température pour une faible humidité."""
        hx = calculer_humidex(20.0, 30.0)
        # À 20°C / 30% HR, l'Humidex est légèrement supérieur à 20°C
        assert 18.0 < hx < 25.0

    def test_valeur_connue(self):
        """Vérifie une valeur calculée manuellement."""
        # À 30°C / 60% HR, la valeur attendue est ~38.29
        hx = calculer_humidex(30.0, 60.0)
        assert abs(hx - 38.29) < 0.5

    def test_retour_float(self):
        """Le résultat doit être un float."""
        assert isinstance(calculer_humidex(25.0, 50.0), float)

    def test_arrondi_deux_decimales(self):
        """Le résultat doit être arrondi à 2 décimales."""
        hx = calculer_humidex(25.0, 50.0)
        assert round(hx, 2) == hx

    def test_temperature_limite_basse(self):
        """La température minimale valide est -50°C."""
        hx = calculer_humidex(-50.0, 50.0)
        assert isinstance(hx, float)

    def test_temperature_limite_haute(self):
        """La température maximale valide est 60°C."""
        hx = calculer_humidex(60.0, 50.0)
        assert isinstance(hx, float)

    def test_humidite_zero(self):
        """Humidité 0% : le Humidex doit être inférieur à la température."""
        hx = calculer_humidex(30.0, 0.0)
        assert hx < 30.0

    def test_humidite_cent(self):
        """Humidité 100% : le Humidex doit être nettement supérieur à la température."""
        hx = calculer_humidex(30.0, 100.0)
        assert hx > 35.0

    @pytest.mark.parametrize("temperature", [-51.0, 61.0, 100.0, -100.0])
    def test_temperature_hors_plage_leve_valueerror(self, temperature: float):
        """Une température hors plage doit lever ValueError."""
        with pytest.raises(ValueError, match="Température hors plage"):
            calculer_humidex(temperature, 50.0)

    @pytest.mark.parametrize("humidite", [-1.0, 101.0, 200.0])
    def test_humidite_hors_plage_leve_valueerror(self, humidite: float):
        """Une humidité hors plage doit lever ValueError."""
        with pytest.raises(ValueError, match="Humidité relative hors plage"):
            calculer_humidex(25.0, humidite)


# ---------------------------------------------------------------------------
# classe_depuis_humidex
# ---------------------------------------------------------------------------


class TestClasseDepuisHumidex:
    """Tests de la correspondance Humidex → classe de vivabilité."""

    @pytest.mark.parametrize("humidex,expected_classe", [
        (10.0, 0),   # HX < 25 → Conditions Normales
        (24.9, 0),
        (25.0, 1),   # 25 ≤ HX < 30 → Gêne légère
        (29.9, 1),
        (30.0, 2),   # 30 ≤ HX < 34 → Vigilance
        (33.9, 2),
        (34.0, 3),   # 34 ≤ HX < 38 → Inconfort évident
        (37.9, 3),
        (38.0, 4),   # 38 ≤ HX < 40 → Alerte
        (39.9, 4),
        (40.0, 5),   # 40 ≤ HX < 43 → Inconfort intense
        (42.9, 5),
        (43.0, 6),   # 43 ≤ HX < 45 → Urgence Vitale
        (44.9, 6),
        (45.0, 7),   # HX ≥ 45 → Danger Extrême
        (60.0, 7),
    ])
    def test_correspondance_seuils(self, humidex: float, expected_classe: int):
        """Vérifie la correspondance exacte Humidex → classe pour chaque seuil."""
        assert classe_depuis_humidex(humidex) == expected_classe

    def test_retour_int(self):
        """La classe retournée doit être un entier."""
        assert isinstance(classe_depuis_humidex(30.0), int)

    def test_plage_valide(self):
        """La classe doit toujours être dans [0, 7]."""
        for hx in [-10.0, 0.0, 20.0, 35.0, 50.0, 100.0]:
            classe = classe_depuis_humidex(hx)
            assert 0 <= classe <= 7
