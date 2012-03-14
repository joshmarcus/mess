ALTER TABLE membership_member ADD COLUMN referral_source varchar(20) NULL;
ALTER TABLE membership_member ADD COLUMN referring_member_id integer NULL;
ALTER TABLE membership_member ADD COLUMN orientation_id integer REFERENCES "events_orientation" ("event_ptr_id") DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE "membership_member" ADD CONSTRAINT "referring_member_id_refs_id_1b91cc7d" FOREIGN KEY ("referring_member_id") REFERENCES "membership_member" ("id") DEFERRABLE INITIALLY DEFERRED;
