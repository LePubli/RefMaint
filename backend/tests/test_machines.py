"""Tests CRUD machines."""
import pytest


class TestMachinesCRUD:
    def test_list_machines(self, client, admin_headers, machine_id):
        res = client.get("/api/machines/", headers=admin_headers)
        assert res.status_code == 200
        assert len(res.json()) >= 1

    def test_get_machine_by_id(self, client, admin_headers, machine_id):
        res = client.get(f"/api/machines/{machine_id}", headers=admin_headers)
        assert res.status_code == 200
        assert res.json()["id"] == machine_id
        assert res.json()["nom"] == "Convoyeur A"

    def test_get_machine_not_found(self, client, admin_headers):
        res = client.get("/api/machines/99999", headers=admin_headers)
        assert res.status_code == 404

    def test_create_machine_generates_qr(self, client, admin_headers):
        res = client.post(
            "/api/machines/",
            json={"nom": "Trieur B", "site": "Usine 2"},
            headers=admin_headers,
        )
        assert res.status_code == 200
        data = res.json()
        assert data["qr_code"] is not None
        assert data["qr_code"].startswith("data:image/png;base64,")

    def test_update_machine(self, client, admin_headers, machine_id):
        res = client.put(
            f"/api/machines/{machine_id}",
            json={"statut": "en_panne"},
            headers=admin_headers,
        )
        assert res.status_code == 200
        assert res.json()["statut"] == "en_panne"

    def test_technicien_cannot_create_machine(self, client, technicien_headers):
        res = client.post(
            "/api/machines/",
            json={"nom": "Forbidden", "site": "Usine 1"},
            headers=technicien_headers,
        )
        assert res.status_code == 403

    def test_technicien_cannot_delete_machine(self, client, technicien_headers, machine_id):
        res = client.delete(f"/api/machines/{machine_id}", headers=technicien_headers)
        assert res.status_code == 403

    def test_delete_machine(self, client, admin_headers, machine_id):
        res = client.delete(f"/api/machines/{machine_id}", headers=admin_headers)
        assert res.status_code == 200
        # Vérifie qu'on ne peut plus le récupérer.
        res = client.get(f"/api/machines/{machine_id}", headers=admin_headers)
        assert res.status_code == 404

    def test_filter_by_ligne(self, client, admin_headers):
        # Crée deux machines sur des lignes différentes
        client.post("/api/machines/", json={"nom": "M1", "ligne": "L1"}, headers=admin_headers)
        client.post("/api/machines/", json={"nom": "M2", "ligne": "L2"}, headers=admin_headers)
        res = client.get("/api/machines/?ligne=L1", headers=admin_headers)
        assert res.status_code == 200
        assert all(m["ligne"] == "L1" for m in res.json())
