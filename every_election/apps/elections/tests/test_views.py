from django.test import TestCase
from elections.tests.factories import ElectionWithStatusFactory, related_status


class TestSingleElectionView(TestCase):

    def test_election_status(self):
        # 4 ballots with different moderation statuses
        approved = ElectionWithStatusFactory(group=None, moderation_status=related_status('Approved'))
        suggested = ElectionWithStatusFactory(group=None, moderation_status=related_status('Suggested'))
        rejected = ElectionWithStatusFactory(group=None, moderation_status=related_status('Rejected'))
        deleted = ElectionWithStatusFactory(group=None, moderation_status=related_status('Deleted'))

        # approved elections shoud be visible via the DetailView
        resp = self.client.get("/elections/{}/".format(approved.election_id))
        self.assertEqual(200, resp.status_code)

        # we shouldn't be able to access elections which are
        # suggsted, rejected or deleted via the DetailView
        resp = self.client.get("/api/elections/{}/".format(rejected.election_id))
        self.assertEqual(404, resp.status_code)
        resp = self.client.get("/api/elections/{}/".format(suggested.election_id))
        self.assertEqual(404, resp.status_code)
        resp = self.client.get("/api/elections/{}/".format(deleted.election_id))
        self.assertEqual(404, resp.status_code)

    def test_child_election_status(self):
        # 4 ballots in the same group with different moderation statuses
        group = ElectionWithStatusFactory(group_type='election', moderation_status=related_status('Approved'))
        approved = ElectionWithStatusFactory(group=group, moderation_status=related_status('Approved'))
        suggested = ElectionWithStatusFactory(group=group, moderation_status=related_status('Suggested'))
        rejected = ElectionWithStatusFactory(group=group, moderation_status=related_status('Rejected'))
        deleted = ElectionWithStatusFactory(group=group, moderation_status=related_status('Deleted'))

        # DetailView should only show approved child elections
        resp = self.client.get("/elections/{}/".format(group.election_id))
        self.assertEqual(200, resp.status_code)
        self.assertContains(resp, approved.election_id, html=True)
        self.assertNotContains(resp, suggested.election_id, html=True)
        self.assertNotContains(resp, rejected.election_id, html=True)
        self.assertNotContains(resp, deleted.election_id, html=True)
