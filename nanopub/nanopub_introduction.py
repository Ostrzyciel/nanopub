# -*- coding: utf-8 -*-
"""This module includes a client for the nanopub server.
"""

from rdflib import Graph, Literal, Namespace, URIRef, ConjunctiveGraph, BNode
from rdflib.namespace import DC, DCTERMS, PROV, RDF, RDFS, VOID, XSD, FOAF
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

from nanopub.definitions import log
from nanopub.profile import Profile
from nanopub.nanopublication import Nanopublication
from nanopub.namespaces import NPX
from nanopub.nanopub_config import NanopubConfig


class NanopubIntroduction(Nanopublication):
    """
    Publish a Nanopub introduction to introduce a key pair for an ORCID

    Args:
        np_list: List of nanopub URIs
        title: Title of the Nanopub Index
        description: Description of the Nanopub Index
        creation_time: Creation time of the Nanopub Index, in format YYYY-MM-DDThh-mm-ss
        creators: List of the ORCID of the creators of the Nanopub Index
        see_also: A URL to a page with further information on the Nanopub Index
    """

    def __init__(
        self,
        public_key: str = None,
        profile: Profile = None,
        config: NanopubConfig = NanopubConfig(
            add_prov_generated_time=False,
            add_pubinfo_generated_time=True,
            attribute_publication_to_profile=True,
            attribute_assertion_to_profile=True,
        ),
    ) -> None:
        super().__init__(
            profile=profile,
            config=config,
        )

        if not public_key:
            log.info("Generating private/public pair keys")
            public_key = self._generate_keys()

        key_declaration = BNode('keyDeclaration')
        orcid_node = URIRef(self.profile.orcid_id)

        self.assertion.add((key_declaration, NPX.declaredBy, orcid_node))
        self.assertion.add((key_declaration, NPX.hasAlgorithm, Literal("RSA")))
        self.assertion.add((key_declaration, NPX.hasPublicKey, Literal(public_key)))
        self.assertion.add((orcid_node, FOAF.name, Literal(self.profile.name)))


    def _generate_keys(self) -> str:
        # Generate private/public RSA key pair
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )

        unencrypted_pem_private_key = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        )
        pem_public_key = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        # Store key pair
        private_key_file = open(self.profile.private_key, "w")
        private_key_file.write(unencrypted_pem_private_key.decode())
        private_key_file.close()
        public_key_file = open(self.profile.public_key, "w")
        public_key_file.write(pem_public_key.decode())
        public_key_file.close()
        return pem_public_key.decode()
