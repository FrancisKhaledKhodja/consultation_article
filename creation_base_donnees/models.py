from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import LargeBinary


class ArticleManufacturer(SQLModel, table=True):
    """Table d'association entre Article et Manufacturer"""
    id: Optional[int] = Field(default=None, primary_key=True)
    code_article: str = Field(foreign_key="article.code_article")
    nom_fabricant: Optional[str] = None 
    reference_article_fabricant: Optional[str] = None
    
    # Relation avec Article
    article: "Article" = Relationship(back_populates="fabricants")


class Article(SQLModel, table=True):
    """Modèle pour les articles"""
    
    # Champs d'identification
    code_article: str = Field(unique=True, index=True, primary_key=True)
    proprietaire_article: str = Field(index=True)
    type_article: Optional[str] = Field(default="", index=True)
    
    # Libellés et descriptions
    libelle_court_article: str
    libelle_long_article: Optional[str] = None
    description_famille_d_achat: Optional[str] = None
    commentaire_technique: Optional[str] = None
    commentaire_logistique: Optional[str] = None
    
    # Statut et cycle de vie
    statut_abrege_article: Optional[str] = None
    cycle_de_vie_achat: Optional[str] = None
    cycle_de_vie_de_production_pim: Optional[str] = None
    
    # Catalogue et classification
    feuille_du_catalogue: Optional[str] = Field(default=None, index=True)
    description_de_la_feuille_du_catalogue: Optional[str] = None
    famille_d_achat_feuille_du_catalogue: Optional[str] = None
    catalogue_consommable: Optional[str] = None
    criticite_pim: Optional[str] = None
    famille_immobilisation: Optional[str] = None
    categorie_immobilisation: Optional[str] = None
    categorie_inv_accounting: Optional[str] = None
    
    # Caractéristiques techniques
    suivi_par_num_serie_oui_non: Optional[bool] = Field(default=False)
    stocksecu_inv_oui_non: Optional[bool] = Field(default=False)
    article_hors_normes: Optional[bool] = Field(default=False)
    peremption: Optional[bool] = Field(default=False)
    retour_production: Optional[bool] = Field(default=False)
    is_oc: bool = Field(default=False)
    is_ol: bool = Field(default=False)
    a_retrofiter: Optional[bool] = Field(default=False)
    
    # Caractéristiques logistiques
    affretement: Optional[bool] = Field(default=False)
    fragile: Optional[bool] = Field(default=False)
    poids_article: Optional[float] = None
    volume_article: Optional[float] = None
    hauteur_article: Optional[float] = None
    longueur_article: Optional[float] = None
    largeur_article: Optional[float] = None
    matiere_dangereuse: Optional[bool] = Field(default=False)
    md_code_onu: Optional[str] = None
    md_groupe_emballage: Optional[str] = None
    md_type_colis: Optional[str] = None
    
    # Prix et informations financières
    prix_achat_prev: Optional[float] = None
    pump: Optional[float] = None
    prix_eur_catalogue_article: Optional[float] = None
    compte_cg_achat: Optional[str] = None
    
    # Informations logistiques
    delai_approvisionnement: Optional[int] = None
    delai_de_reparation_contractuel: Optional[int] = None
    point_de_commande: Optional[int] = None
    quantite_a_commander: Optional[int] = None
    qte_cde_minimum_point_de_reappro: Optional[int] = None
    qte_minimum_ordre_de_commande: Optional[int] = None
    qte_maximum_ordre_de_commande: Optional[int] = None
    qte_min_de_l_article: Optional[int] = None
    qte_max_de_l_article: Optional[int] = None
    qte_cde_maximum_quantite_d_ordre_de_commande: Optional[int] = None
    
    # Réparation et maintenance
    lieu_de_reparation_pim: Optional[str] = None
    description_lieu_de_reparation: Optional[str] = None
    rma: Optional[str] = None
    role_responsable_et_equipement: Optional[str] = None
    mnemonique: Optional[str] = None
    
    # Métadonnées
    date_creation_article: Optional[datetime] = None
    nom_createur_article: Optional[str] = None
    date_derniere_modif_article: Optional[datetime] = None
    auteur_derniere_modif_article: Optional[str] = None
    
    # Relations
    fabricants: List["ArticleManufacturer"] = Relationship(back_populates="article")


class Nomenclature(SQLModel, table=True):
    id : int = Field(default=None, primary_key=True)
    """Modèle pour les nomenclatures d'articles"""
    code_article_parent: str = Field(foreign_key="article.code_article")
    code_article_fils: str = Field(foreign_key="article.code_article")
    quantite: float


class Image(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    code_article: str = Field(foreign_key="article.code_article")
    image: bytes = Field(sa_column=Column(LargeBinary))