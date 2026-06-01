"""Subject API 端点测试。"""


class TestListSubjects:
    """GET /api/subjects 测试。"""

    def test_empty_list(self, client):
        """空数据库返回空列表。"""
        resp = client.get("/api/subjects")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 0
        assert data["items"] == []

    def test_with_type_filter(self, client, sample_subject):
        """按类型筛选。"""
        # 类型匹配
        resp = client.get("/api/subjects?type=2")
        assert resp.status_code == 200
        assert resp.json()["total"] == 1

        # 类型不匹配
        resp = client.get("/api/subjects?type=1")
        assert resp.status_code == 200
        assert resp.json()["total"] == 0

    def test_search(self, client, sample_subject):
        """关键词搜索。"""
        # 搜索中文名
        resp = client.get("/api/subjects?search=测试")
        assert resp.status_code == 200
        assert resp.json()["total"] >= 1

        # 搜索不存在的词
        resp = client.get("/api/subjects?search=不存在的词xyz")
        assert resp.status_code == 200
        assert resp.json()["total"] == 0

    def test_year_filter(self, client, sample_subject):
        """年份筛选。"""
        # 在范围内（sample 日期为 2024-01-01）
        resp = client.get("/api/subjects?year=2024")
        assert resp.status_code == 200
        assert resp.json()["total"] == 1

        # 在范围外
        resp = client.get("/api/subjects?year=2025")
        assert resp.status_code == 200
        assert resp.json()["total"] == 0

    def test_score_range(self, client, sample_subject):
        """评分范围筛选。"""
        resp = client.get("/api/subjects?score_from=8&score_to=9")
        assert resp.status_code == 200
        assert resp.json()["total"] == 1

        resp = client.get("/api/subjects?score_from=9&score_to=10")
        assert resp.status_code == 200
        assert resp.json()["total"] == 0

    def test_pagination(self, client, sample_subject):
        """分页参数。"""
        resp = client.get("/api/subjects?page=1&limit=10")
        assert resp.status_code == 200
        data = resp.json()
        assert data["page"] == 1
        assert data["limit"] == 10
        assert len(data["items"]) <= 10

    def test_sort_by_score(self, client, sample_subject):
        """按评分排序。"""
        resp = client.get("/api/subjects?sort=score&order=desc")
        assert resp.status_code == 200
        items = resp.json()["items"]
        if len(items) > 1:
            assert items[0]["score"] >= items[1]["score"]

    def test_nsfw_filter(self, client, sample_subject):
        """NSFW 过滤。"""
        resp = client.get("/api/subjects?nsfw=false")
        assert resp.status_code == 200
        assert resp.json()["total"] == 1

        resp = client.get("/api/subjects?nsfw=true")
        assert resp.status_code == 200
        assert resp.json()["total"] == 0

    def test_series_filter(self, client, sample_subject):
        """系列筛选。"""
        resp = client.get("/api/subjects?series=true")
        assert resp.status_code == 200
        assert resp.json()["total"] == 1

    def test_bangumi_id_in_response(self, client, sample_subject):
        """响应中包含 bangumi_id。"""
        resp = client.get("/api/subjects?type=2")
        item = resp.json()["items"][0]
        assert item["bangumi_id"] == sample_subject.bangumi_id
        assert item["name_cn"] == "测试动画"


class TestGetSubject:
    """GET /api/subjects/{bangumi_id} 测试。"""

    def test_not_found(self, client):
        """不存在的条目返回 404。"""
        resp = client.get("/api/subjects/99999")
        assert resp.status_code == 404

    def test_subject_detail(self, client, sample_subject, sample_episode):
        """详情包含关联数据。"""
        resp = client.get(f"/api/subjects/{sample_subject.bangumi_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["name_cn"] == "测试动画"
        assert data["score"] == 8.5
        assert data["rank"] == 100
        assert data["infobox_raw"] == "Infobox test"
        assert data["infobox_parsed"]["type"] == "动画"
        # 关联数据
        assert len(data["episodes"]) == 1
        assert data["episodes"][0]["name"] == "第1话"
        assert data["episodes"][0]["bangumi_id"] == 1001
