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
        values = []
        for field in self._meta.fields:
            field_name = field.verbose_name
            field_value = getattr(self, field.name)
            values.append(f"{field_name}: {field_value}")
        return " | ".join(values)

    def save(self, *args, **kwargs):
        """Calcola automaticamente il codice fiscale solo se cambiano i dati rilevanti."""
        dati_per_cf = (
            self.nome,
            self.cognome,
            self.sesso,
            self.data_di_nascita,
            self.luogo_di_nascita,
        )  # campi per calcolare il codice fiscale

        # Controlla se è una nuova istanza o se i dati chiave sono cambiati
        if (
            not self.pk
        ):  # se non c'è la primary key, vuol dire che è una nuova scrittura
            deve_calcolare = True
        else:
            vecchia = Anagrafica.objects.get(pk=self.pk)
            vecchi_dati = (
                vecchia.nome,
                vecchia.cognome,
                vecchia.sesso,
                vecchia.data_di_nascita,
                vecchia.luogo_di_nascita,
            )
            # se stiamo modificando, cerca differenze tra vecchi e nuovi dati per il cf
            deve_calcolare = dati_per_cf != vecchi_dati

        if deve_calcolare:  # se è nuova o ci sono modifiche nei dati del cf
            try:
                data_per_cf = self.data_di_nascita.strftime(
                    "%Y-%m-%d"
                )  # inverto la scrittura della data
                self.codice_fiscale = codicefiscale.encode(
                    lastname=self.cognome,
                    firstname=self.nome,
                    gender=self.sesso.lower(),  # type: ignore
                    birthdate=data_per_cf,
                    birthplace=self.luogo_di_nascita,
                )
            except Exception as e:
                print(f"Errore nel calcolo del codice fiscale: {e}")
                self.codice_fiscale = "Non riesco a calcolarlo"

        super().save(*args, **kwargs)
