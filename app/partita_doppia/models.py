from django.db import models
from codicefiscale import codicefiscale

# Create your models here.


class Anagrafica(models.Model):
    TIPO_SCELTE = [
        ("S", "Socio"),
        ("V", "Volontario"),
        ("C", "Consigliere"),
        ("F", "Fornitore"),
    ]

    SESSO = [("M", "Maschio"), ("F", "Femmina")]

    tipo = models.CharField(max_length=1, choices=TIPO_SCELTE)  # cosa sto registrando
    cognome = models.CharField(
        max_length=255,
    )
    nome = models.CharField(
        max_length=255,
    )
    sesso = models.CharField(max_length=1, choices=SESSO)
    data_di_nascita = models.DateField()
    luogo_di_nascita = models.CharField(
        max_length=255,
    )
    codice_fiscale = models.CharField(
        max_length=16, editable=False, blank=True, null=True
    )
    ragione_sociale = models.CharField(max_length=255, blank=True, null=True)

    partita_iva = models.CharField(max_length=20, blank=True, null=True)
    indirizzo = models.CharField(max_length=255, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Anagrafiche"

    def __str__(self):
        return f"{self.ragione_sociale} ({self.get_tipo_display()})"

    def save(self, *args, **kwargs):
        """
        Calcola automaticamente il codice fiscale prima di salvare.
        """
        try:

            # Se l'utente ha inserito la data nel formato italiano gg-mm-aaaa
            # data_str = self.data_di_nascita.strftime("%d-%m-%Y")  # '04-05-1999'

            # Ora inverti la data nel formato richiesto da codicefiscale
            data_per_cf = self.data_di_nascita.strftime("%Y-%m-%d")  # '1999-05-04'

            self.codice_fiscale = codicefiscale.encode(
                lastname=self.cognome,
                firstname=self.nome,
                gender=self.sesso.lower(),
                birthdate=data_per_cf,  # usa il formato corretto
                birthplace=self.luogo_di_nascita,
            )
        except Exception as e:
            # In caso di errore, puoi decidere di lasciarlo vuoto
            print(f"Errore nel calcolo del codice fiscale: {e}")
            self.codice_fiscale = "Non riesco a calcolarlo"

        super().save(*args, **kwargs)
