DROP TABLE IF EXISTS contrats;
DROP TABLE IF EXISTS releves_index;
DROP TABLE IF EXISTS factures;
DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS post;

CREATE TABLE contrats (
    Nr_contrat INTEGER PRIMARY KEY,
    nom_abonne TEXT NOT NULL,
    Adresse TEXT NOT NULL,
    date_contrat DATE NOT NULL DEFAULT CURRENT_DATE,
    Secteur INTEGER NOT NULL,
    Puissance_souscrite INTEGER NOT NULL CHECK(Puissance_souscrite > 0),
    Puissance_installee INTEGER NOT NULL CHECK(Puissance_installee > 0),
    type_installation INTEGER NOT NULL CHECK(type_installation IN (1, 2, 12))
);

CREATE TABLE releves_index (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    Nr_contrat INTEGER NOT NULL,
    date_releve DATE NOT NULL DEFAULT CURRENT_DATE,
    IEA_HC INTEGER NOT NULL CHECK(IEA_HC >= 0),
    IEA_HP INTEGER NOT NULL CHECK(IEA_HP >= 0),
    IEA_HN INTEGER NOT NULL CHECK(IEA_HN >= 0),
    I_energie_reactif INTEGER CHECK(I_energie_reactif >= 0),
    Puissance_demande INTEGER CHECK(Puissance_demande >= 0),
    FOREIGN KEY (Nr_contrat) REFERENCES contrats(Nr_contrat) ON DELETE CASCADE,
    UNIQUE(Nr_contrat, date_releve)
);

CREATE TABLE factures (
    id INTEGER PRIMARY KEY,
    Nr_contrat INTEGER NOT NULL,
    releve_id INTEGER UNIQUE NOT NULL,
    date_emission DATE NOT NULL DEFAULT CURRENT_DATE,
    total_a_payer Real NOT NULL,
    total_E_E Integer NOT NULL CHECK(total_E_E >= 0),
    statut TEXT NOT NULL DEFAULT 'encours de traitement' CHECK(statut IN ('encours de traitement','controle', 'validee', 'payee', 'annulee')),
    FOREIGN KEY (Nr_contrat) REFERENCES contrats(Nr_contrat) ON DELETE CASCADE,
    FOREIGN KEY (releve_id) REFERENCES releves_index(id) ON DELETE RESTRICT
);

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE post (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  FOREIGN KEY (author_id) REFERENCES user (id)
);