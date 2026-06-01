"""其他 API 端点冒烟测试。"""


class TestHealth:
    """GET /api/health 测试。"""

    def test_health(self, client):
        resp = client.get("/api/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert "version" in data


class TestEpisodes:
    """GET /api/episodes 测试。"""

    def test_list_by_subject(self, client, sample_subject, sample_episode):
        resp = client.get(f"/api/episodes?subject_id={sample_subject.bangumi_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        assert data["items"][0]["name"] == "第1话"

    def test_get_episode(self, client, sample_episode):
        resp = client.get(f"/api/episodes/{sample_episode.bangumi_id}")
        assert resp.status_code == 200
        assert resp.json()["name"] == "第1话"

    def test_episode_not_found(self, client):
        resp = client.get("/api/episodes/99999")
        assert resp.status_code == 404


class TestPersons:
    """GET /api/persons 测试。"""

    def test_list(self, client, sample_person):
        resp = client.get("/api/persons")
        assert resp.status_code == 200
        assert resp.json()["total"] == 1

    def test_get_person(self, client, sample_person):
        resp = client.get(f"/api/persons/{sample_person.bangumi_id}")
        assert resp.status_code == 200
        assert resp.json()["name"] == "Test Director"

    def test_person_not_found(self, client):
        resp = client.get("/api/persons/99999")
        assert resp.status_code == 404


class TestCharacters:
    """GET /api/characters 测试。"""

    def test_list(self, client, sample_character):
        resp = client.get("/api/characters")
        assert resp.status_code == 200
        assert resp.json()["total"] == 1

    def test_get_character(self, client, sample_character):
        resp = client.get(f"/api/characters/{sample_character.bangumi_id}")
        assert resp.status_code == 200
        assert resp.json()["name"] == "Test Character"

    def test_character_not_found(self, client):
        resp = client.get("/api/characters/99999")
        assert resp.status_code == 404


class TestRelations:
    """关联 API 测试。"""

    def test_subject_relations(self, client, sample_subject):
        resp = client.get(f"/api/subjects/{sample_subject.bangumi_id}/relations")
        assert resp.status_code == 200
        assert "relations" in resp.json()

    def test_subject_characters(self, client, sample_subject):
        resp = client.get(f"/api/subjects/{sample_subject.bangumi_id}/characters")
        assert resp.status_code == 200
        assert "characters" in resp.json()

    def test_subject_persons(self, client, sample_subject):
        resp = client.get(f"/api/subjects/{sample_subject.bangumi_id}/persons")
        assert resp.status_code == 200
        assert "persons" in resp.json()

    def test_relations_not_found(self, client):
        resp = client.get("/api/subjects/99999/relations")
        assert resp.status_code == 404


class TestSearch:
    """GET /api/search 测试。"""

    def test_search_without_query(self, client):
        resp = client.get("/api/search?q=")
        assert resp.status_code == 422

    def test_search_subjects(self, client, sample_subject):
        resp = client.get("/api/search?q=测试&scope=subjects")
        assert resp.status_code == 200
        data = resp.json()
        assert data["scope"] == "subjects"
        assert len(data["results"].get("subjects", [])) >= 1

    def test_search_no_results(self, client):
        resp = client.get("/api/search?q=xyz_nonexistent&scope=subjects")
        assert resp.status_code == 200
        assert len(resp.json()["results"].get("subjects", [])) == 0


class TestSync:
    """同步 API 测试。"""

    def test_sync_status(self, client):
        resp = client.get("/api/sync/status")
        assert resp.status_code == 200
        assert "has_data" in resp.json()
        assert "table_counts" in resp.json()
