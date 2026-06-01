"""UserRecord API 端点测试。"""


class TestCreateRecord:
    """POST /api/records 测试。"""

    def test_create_success(self, client, sample_subject):
        """成功创建观看记录。"""
        resp = client.post(
            "/api/records",
            json={
                "subject_id": sample_subject.bangumi_id,
                "status": 2,
                "progress": 3,
                "rating": 8,
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["subject_id"] == sample_subject.bangumi_id
        assert data["status"] == 2
        assert data["progress"] == 3
        assert data["rating"] == 8
        assert data["id"] is not None

    def test_create_default_status(self, client, sample_subject):
        """默认状态为 1（想看）。"""
        resp = client.post(
            "/api/records",
            json={
                "subject_id": sample_subject.bangumi_id,
                "status": 1,
                "progress": 0,
            },
        )
        assert resp.status_code == 201
        assert resp.json()["status"] == 1

    def test_create_invalid_status(self, client, sample_subject):
        """无效状态返回 422。"""
        resp = client.post(
            "/api/records",
            json={
                "subject_id": sample_subject.bangumi_id,
                "status": 99,
            },
        )
        assert resp.status_code == 422

    def test_create_invalid_rating(self, client, sample_subject):
        """无效评分返回 422。"""
        resp = client.post(
            "/api/records",
            json={
                "subject_id": sample_subject.bangumi_id,
                "status": 1,
                "rating": 99,
            },
        )
        assert resp.status_code == 422


class TestUpdateRecord:
    """PUT /api/records/{id} 测试。"""

    def test_update_success(self, client, sample_subject):
        """成功更新记录。"""
        # 先创建
        create_resp = client.post(
            "/api/records",
            json={"subject_id": sample_subject.bangumi_id, "status": 1},
        )
        record_id = create_resp.json()["id"]

        # 更新
        resp = client.put(
            f"/api/records/{record_id}",
            json={"status": 3, "progress": 12, "rating": 9},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == 3
        assert data["progress"] == 12
        assert data["rating"] == 9

    def test_update_not_found(self, client):
        """更新不存在的记录返回 404。"""
        resp = client.put(
            "/api/records/99999",
            json={"status": 3},
        )
        assert resp.status_code == 404


class TestDeleteRecord:
    """DELETE /api/records/{id} 测试。"""

    def test_delete_success(self, client, sample_subject):
        """成功删除记录。"""
        create_resp = client.post(
            "/api/records",
            json={"subject_id": sample_subject.bangumi_id, "status": 1},
        )
        record_id = create_resp.json()["id"]

        resp = client.delete(f"/api/records/{record_id}")
        assert resp.status_code == 204

        # 确认已删除
        get_resp = client.get("/api/records")
        assert all(r["id"] != record_id for r in get_resp.json())

    def test_delete_not_found(self, client):
        """删除不存在的记录返回 404。"""
        resp = client.delete("/api/records/99999")
        assert resp.status_code == 404


class TestListRecords:
    """GET /api/records 测试。"""

    def test_empty_list(self, client):
        """空记录列表。"""
        resp = client.get("/api/records")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_filter_by_status(self, client, sample_subject):
        """按状态筛选。"""
        client.post(
            "/api/records",
            json={"subject_id": sample_subject.bangumi_id, "status": 2},
        )
        client.post(
            "/api/records",
            json={"subject_id": sample_subject.bangumi_id, "status": 3},
        )

        resp = client.get("/api/records?status=2")
        records = resp.json()
        assert all(r["status"] == 2 for r in records)


class TestRecordsStats:
    """GET /api/records/stats 测试。"""

    def test_stats_empty(self, client):
        """空统计。"""
        resp = client.get("/api/records/stats")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_records"] == 0
        assert isinstance(data["status_distribution"], dict)
        assert isinstance(data["rating_distribution"], dict)

    def test_stats_with_data(self, client, sample_subject):
        """有数据时的统计。"""
        client.post(
            "/api/records",
            json={
                "subject_id": sample_subject.bangumi_id,
                "status": 3,  # 看过
                "rating": 8,
            },
        )
        resp = client.get("/api/records/stats")
        data = resp.json()
        assert data["total_records"] == 1
        assert data["status_distribution"]["看过"] == 1
        assert data["rating_distribution"]["8"] == 1
