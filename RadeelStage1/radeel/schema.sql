DROP TABLE IF EXISTS contrats;
DROP TABLE IF EXISTS releves;
DROP TABLE IF EXISTS factures;
DROP TABLE IF EXISTS user;

CREATE TABLE contrats (
    Nr_contrat INTEGER PRIMARY KEY ,
    nom_abonne TEXT NOT NULL,
    Adresse TEXT NOT NULL,
    date_contrat DATE NOT NULL DEFAULT CURRENT_DATE,
    Secteur INTEGER NOT NULL,
    Puissance_souscrite INTEGER NOT NULL CHECK(Puissance_souscrite > 0),
    Puissance_installee INTEGER NOT NULL CHECK(Puissance_installee > 0),
    type_installation INTEGER NOT NULL CHECK(type_installation IN (1, 2, 12)),
    statut TEXT NOT NULL DEFAULT 'actif' CHECK(statut IN ('actif', 'resile', 'suspendu'))
);

CREATE TABLE releves (
    id TEXT PRIMARY KEY NOT NULL,
    Nr_contrat INTEGER NOT NULL,
    mois INTEGER CHECK (mois BETWEEN 1 AND 12),
    annee INTEGER ,
    IER INTEGER CHECK(IER >= 0),-- Indicateur d'energie reactif
    IEA_HC INTEGER CHECK(IEA_HC >= 0),-- Indicateur d'energie active en heures creuses
    IEA_HN INTEGER CHECK(IEA_HN >= 0),-- Indicateur d'energie active en heures normales
    IEA_HP INTEGER CHECK(IEA_HP >= 0),-- Indicateur d'energie active en heures pleines
    RED_ER INTEGER DEFAULT 0,--Redressement d'energie reactif
    RED_EA_HC INTEGER DEFAULT 0,--Redressement d'energie active en heures creuses
    RED_EA_HN INTEGER DEFAULT 0,--Redressement d'energie active en heures normales
    RED_EA_HP INTEGER DEFAULT 0 ,--Redressement d'energie active en heures pleines
    IMAX INTEGER CHECK(IMAX >= 0),--Indicateur de maximum KW
    FOREIGN KEY (Nr_contrat) REFERENCES contrats(Nr_contrat) ON DELETE CASCADE
    --UNIQUE(Nr_contrat, mois, annee) -- Assure qu'il n'y a qu'un relevé par mois et par contrat
);

CREATE TABLE factures (
    id TEXT PRIMARY KEY NOT NULL,
    Nr_contrat INTEGER NOT NULL,
    date_ DATE NOT NULL DEFAULT CURRENT_DATE,
    total_a_payer Real ,
    total_E_A Integer CHECK(total_E_A >= 0),
    statut TEXT DEFAULT 'encours de traitement' CHECK(statut IN ('encours de traitement','controle', 'validee', 'payee', 'annulee')),
    FOREIGN KEY (Nr_contrat) REFERENCES contrats(Nr_contrat) ON DELETE CASCADE,
    FOREIGN KEY (id) REFERENCES releves(id) ON DELETE RESTRICT
);

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);