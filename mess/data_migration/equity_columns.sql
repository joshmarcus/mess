alter table membership_member add column "equity_held" numeric(8,2) NOT NULL DEFAULT 0.00;
alter table membership_member add column "equity_due" numeric(8,2) NOT NULL DEFAULT 0.00;
alter table membership_member add column "equity_increment" numeric(8,2) NOT NULL DEFAULT 25.00;
alter table membership_account add column "shared_address" boolean NOT NULL DEFAULT 0;
alter table accounting_transaction add column "is4c_timestamp" datetime; 
