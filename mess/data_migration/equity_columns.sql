alter table membership_member add column "equity_held" decimal NOT NULL DEFAULT 0;
alter table membership_member add column "equity_due" decimal NOT NULL DEFAULT 0;
alter table membership_member add column "equity_increment" decimal NOT NULL DEFAULT 25;
alter table membership_account add column "shared_address" bool NOT NULL DEFAULT 0;
alter table accounting_transaction add column "is4c_timestamp" datetime; 
