"""Tests RBAC : vérifie que les techniciens ne peuvent pas modifier/supprimer,
et que les managers/admins le peuvent."""
import pytest


# ── PANNES ──────────────────────────────────────────────────────────────────

class TestPannesRBAC:
    def test_technicien_can_create_panne(self, client, technicien_headers, machine_id):
        res = client.post(
            "/api/pannes/",
            json={"machine_id": machine_id, "titre": "Bruit anormal", "criticite": 3},
            headers=technicien_headers,
        )
        assert res.status_code == 200

    def test_technicien_cannot_update_panne(self, client, technicien_headers, machine_id, admin_headers):
        # Admin crée la panne
        res = client.post(
            "/api/pannes/",
            json={"machine_id": machine_id, "titre": "Panne test", "criticite": 2},
            headers=admin_headers,
        )
        panne_id = res.json()["id"]
        # Technicien tente de modifier
        res = client.put(
            f"/api/pannes/{panne_id}",
            json={"titre": "Modified"},
            headers=technicien_headers,
        )
        assert res.status_code == 403

    def test_technicien_cannot_delete_panne(self, client, technicien_headers, machine_id, admin_headers):
        res = client.post(
            "/api/pannes/",
            json={"machine_id": machine_id, "titre": "Panne a suppr", "criticite": 1},
            headers=admin_headers,
        )
        panne_id = res.json()["id"]
        res = client.delete(f"/api/pannes/{panne_id}", headers=technicien_headers)
        assert res.status_code == 403

    def test_manager_can_update_panne(self, client, manager_headers, machine_id, admin_headers):
        res = client.post(
            "/api/pannes/",
            json={"machine_id": machine_id, "titre": "Panne test", "criticite": 2},
            headers=admin_headers,
        )
        panne_id = res.json()["id"]
        res = client.put(
            f"/api/pannes/{panne_id}",
            json={"titre": "Updated by manager"},
            headers=manager_headers,
        )
        assert res.status_code == 200
        assert res.json()["titre"] == "Updated by manager"

    def test_manager_can_delete_panne(self, client, manager_headers, machine_id, admin_headers):
        res = client.post(
            "/api/pannes/",
            json={"machine_id": machine_id, "titre": "Panne del", "criticite": 1},
            headers=admin_headers,
        )
        panne_id = res.json()["id"]
        res = client.delete(f"/api/pannes/{panne_id}", headers=manager_headers)
        assert res.status_code == 200


# ── INTERVENTIONS ───────────────────────────────────────────────────────────

class TestInterventionsRBAC:
    def test_technicien_can_create_intervention(self, client, technicien_headers, machine_id):
        res = client.post(
            "/api/interventions/",
            json={"machine_id": machine_id, "commentaire": "Intervention terrain"},
            headers=technicien_headers,
        )
        assert res.status_code == 200

    def test_technicien_field_is_forced(self, client, technicien_headers, machine_id):
        """Le technicien ne peut pas usurper l'identité d'un autre utilisateur."""
        res = client.post(
            "/api/interventions/",
            json={"machine_id": machine_id, "commentaire": "Usurpation?"},
            headers=technicien_headers,
        )
        assert res.status_code == 200
        # Le technicien doit être forcé à l'utilisateur courant, pas à la valeur fournie.
        assert res.json()["technicien"] == "tech1"

    def test_technicien_cannot_update_intervention(self, client, technicien_headers, machine_id, admin_headers):
        res = client.post(
            "/api/interventions/",
            json={"machine_id": machine_id, "commentaire": "Test"},
            headers=admin_headers,
        )
        inter_id = res.json()["id"]
        res = client.put(
            f"/api/interventions/{inter_id}",
            json={"commentaire": "Hacked"},
            headers=technicien_headers,
        )
        assert res.status_code == 403

    def test_technicien_cannot_delete_intervention(self, client, technicien_headers, machine_id, admin_headers):
        res = client.post(
            "/api/interventions/",
            json={"machine_id": machine_id, "commentaire": "Test"},
            headers=admin_headers,
        )
        inter_id = res.json()["id"]
        res = client.delete(f"/api/interventions/{inter_id}", headers=technicien_headers)
        assert res.status_code == 403

    def test_technicien_cannot_validate_intervention(self, client, technicien_headers, machine_id, admin_headers):
        res = client.post(
            "/api/interventions/",
            json={"machine_id": machine_id, "commentaire": "Test"},
            headers=admin_headers,
        )
        inter_id = res.json()["id"]
        res = client.post(
            f"/api/interventions/{inter_id}/valider",
            headers=technicien_headers,
        )
        assert res.status_code == 403

    def test_manager_can_validate_intervention(self, client, manager_headers, machine_id, admin_headers):
        res = client.post(
            "/api/interventions/",
            json={"machine_id": machine_id, "commentaire": "Test"},
            headers=admin_headers,
        )
        inter_id = res.json()["id"]
        res = client.post(
            f"/api/interventions/{inter_id}/valider",
            headers=manager_headers,
        )
        assert res.status_code == 200
        assert res.json()["validee"] is True


# ── PIÈCES ───────────────────────────────────────────────────────────────────

class TestPiecesRBAC:
    def test_technicien_can_create_piece(self, client, technicien_headers):
        res = client.post(
            "/api/pieces/",
            json={"reference": "REF-001", "nom": "Roulement", "stock": 10},
            headers=technicien_headers,
        )
        assert res.status_code == 200

    def test_technicien_cannot_update_piece(self, client, technicien_headers, admin_headers):
        res = client.post(
            "/api/pieces/",
            json={"reference": "REF-002", "nom": "Courroie", "stock": 5},
            headers=admin_headers,
        )
        piece_id = res.json()["id"]
        res = client.put(
            f"/api/pieces/{piece_id}",
            json={"nom": "Hacked"},
            headers=technicien_headers,
        )
        assert res.status_code == 403

    def test_technicien_cannot_delete_piece(self, client, technicien_headers, admin_headers):
        res = client.post(
            "/api/pieces/",
            json={"reference": "REF-003", "nom": "Joint", "stock": 2},
            headers=admin_headers,
        )
        piece_id = res.json()["id"]
        res = client.delete(f"/api/pieces/{piece_id}", headers=technicien_headers)
        assert res.status_code == 403


# ── MAINTENANCE PRÉVENTIVE ─────────────────────────────────────────────────

class TestMaintenanceRBAC:
    def test_technicien_can_create_maintenance(self, client, technicien_headers, machine_id):
        res = client.post(
            "/api/maintenance-preventive/",
            json={"machine_id": machine_id, "titre": "Graissage", "frequence_jours": 30},
            headers=technicien_headers,
        )
        assert res.status_code == 200

    def test_technicien_cannot_update_maintenance(self, client, technicien_headers, machine_id, admin_headers):
        res = client.post(
            "/api/maintenance-preventive/",
            json={"machine_id": machine_id, "titre": "Maint test", "frequence_jours": 90},
            headers=admin_headers,
        )
        mp_id = res.json()["id"]
        res = client.put(
            f"/api/maintenance-preventive/{mp_id}",
            json={"titre": "Hacked"},
            headers=technicien_headers,
        )
        assert res.status_code == 403

    def test_technicien_cannot_delete_maintenance(self, client, technicien_headers, machine_id, admin_headers):
        res = client.post(
            "/api/maintenance-preventive/",
            json={"machine_id": machine_id, "titre": "Maint del", "frequence_jours": 60},
            headers=admin_headers,
        )
        mp_id = res.json()["id"]
        res = client.delete(f"/api/maintenance-preventive/{mp_id}", headers=technicien_headers)
        assert res.status_code == 403

    def test_technicien_cannot_mark_effectue(self, client, technicien_headers, machine_id, admin_headers):
        res = client.post(
            "/api/maintenance-preventive/",
            json={"machine_id": machine_id, "titre": "Maint eff", "frequence_jours": 30},
            headers=admin_headers,
        )
        mp_id = res.json()["id"]
        res = client.post(
            f"/api/maintenance-preventive/{mp_id}/effectuer",
            headers=technicien_headers,
        )
        assert res.status_code == 403
