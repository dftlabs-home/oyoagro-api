"""
FILE: src/shared/models.py
Database models - Maps to existing oyoagrodb PostgreSQL database
"""
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime, date
from decimal import Decimal
from uuid import UUID


class TimestampModel(SQLModel):
    """Base model with timestamps"""
    createdat: Optional[datetime] = Field(default=None, nullable=True)
    updatedat: Optional[datetime] = Field(default=None, nullable=True)
    deletedat: Optional[datetime] = Field(default=None, nullable=True)


class VersionedModel(TimestampModel):
    """Base model with versioning"""
    version: Optional[int] = Field(default=None, nullable=True)


# USER MODELS
class Useraccount(TimestampModel, table=True):
    __tablename__ = "useraccount" # type: ignore
    userid: Optional[int] = Field(default=None, primary_key=True)
    tempclientid: Optional[UUID] = Field(default=None, nullable=True)
    username: Optional[str] = Field(default=None, nullable=True)
    passwordhash: Optional[str] = Field(default=None, nullable=True)
    password: Optional[str] = Field(default=None, nullable=True)
    salt: Optional[str] = Field(default=None, nullable=True)
    email: Optional[str] = Field(default=None, nullable=True)
    status: Optional[int] = Field(default=None, nullable=True)
    apitoken: Optional[str] = Field(default=None, nullable=True)
    logincount: Optional[int] = Field(default=None, nullable=True)
    lastlogindate: Optional[date] = Field(default=None, nullable=True)
    deactivateddate: Optional[date] = Field(default=None, nullable=True)
    failedloginattempt: Optional[int] = Field(default=None, nullable=True)
    securityquestion: Optional[str] = Field(default=None, nullable=True)
    securityanswer: Optional[str] = Field(default=None, nullable=True)
    isactive: Optional[bool] = Field(default=None, nullable=True)
    islocked: Optional[bool] = Field(default=None, nullable=True)
    passwordresettoken: Optional[str] = Field(default=None, nullable=True)
    lastpasswordreset: Optional[datetime] = Field(default=None, nullable=True)
    passwordresettokenexpires: Optional[datetime] = Field(default=None, nullable=True)
    version: Optional[int] = Field(default=None, nullable=True)
    lgaid: Optional[int] = Field(default=None, nullable=True)


class Userprofile(VersionedModel, table=True):
    __tablename__ = "userprofile" # type: ignore
    userprofileid: Optional[int] = Field(default=None, primary_key=True)
    tempclientid: Optional[UUID] = Field(default=None, nullable=True)
    userid: Optional[int] = Field(default=None, foreign_key="useraccount.userid")
    firstname: Optional[str] = Field(default=None, nullable=True)
    middlename: Optional[str] = Field(default=None, nullable=True)
    lastname: Optional[str] = Field(default=None, nullable=True)
    designation: Optional[str] = Field(default=None, nullable=True)
    gender: Optional[str] = Field(default=None, nullable=True)
    email: Optional[str] = Field(default=None, nullable=True)
    phonenumber: Optional[str] = Field(default=None, nullable=True)
    photo: Optional[str] = Field(default=None, nullable=True)
    roleid: Optional[int] = Field(default=None, nullable=True)
    lgaid: Optional[int] = Field(default=None, nullable=True)


class PasswordResetToken(TimestampModel, table=True):
    __tablename__ = "passwordresettokens" # type: ignore
    id: Optional[int] = Field(default=None, primary_key=True)
    userid: Optional[int] = Field(default=None, foreign_key="useraccount.userid")
    token: Optional[str] = Field(default=None, nullable=True)
    expiresat: Optional[datetime] = Field(default=None, nullable=True)
    isused: Optional[bool] = Field(default=None, nullable=True)
    usedat: Optional[datetime] = Field(default=None, nullable=True)
    ipaddress: Optional[str] = Field(default=None, nullable=True)
    useragent: Optional[str] = Field(default=None, nullable=True)


# GEOGRAPHICAL MODELS
class Region(VersionedModel, table=True):
    __tablename__ = "region" # type: ignore
    regionid: Optional[int] = Field(default=None, primary_key=True)
    tempclientid: Optional[UUID] = Field(default=None, nullable=True)
    regionname: Optional[str] = Field(default=None, nullable=True)


class Lga(VersionedModel, table=True):
    __tablename__ = "lga" # type: ignore
    lgaid: Optional[int] = Field(default=None, primary_key=True)
    tempclientid: Optional[UUID] = Field(default=None, nullable=True)
    lganame: Optional[str] = Field(default=None, nullable=True)
    regionid: Optional[int] = Field(default=None, foreign_key="region.regionid")


class Address(VersionedModel, table=True):
    __tablename__ = "addresses" # type: ignore
    addressid: Optional[int] = Field(default=None, primary_key=True)
    tempclientid: Optional[UUID] = Field(default=None, nullable=True)
    streetaddress: Optional[str] = Field(default=None, nullable=True)
    town: Optional[str] = Field(default=None, nullable=True)
    postalcode: Optional[str] = Field(default=None, nullable=True)
    lgaid: Optional[int] = Field(default=None, foreign_key="lga.lgaid")
    latitude: Optional[Decimal] = Field(default=None, nullable=True)
    longitude: Optional[Decimal] = Field(default=None, nullable=True)
    userid: Optional[int] = Field(default=None, nullable=True)
    farmerid: Optional[int] = Field(default=None, nullable=True)
    farmid: Optional[int] = Field(default=None, nullable=True)


class Userregion(VersionedModel, table=True):
    __tablename__ = "userregion" # type: ignore
    userregionid: Optional[int] = Field(default=None, primary_key=True)
    tempclientid: Optional[UUID] = Field(default=None, nullable=True)
    userid: Optional[int] = Field(default=None, foreign_key="useraccount.userid")
    regionid: Optional[int] = Field(default=None, foreign_key="region.regionid")


# FARMER & FARM MODELS
class Association(VersionedModel, table=True):
    __tablename__ = "association" # type: ignore
    associationid: Optional[int] = Field(default=None, primary_key=True)
    tempclientid: Optional[UUID] = Field(default=None, nullable=True)
    name: Optional[str] = Field(default=None, nullable=True)
    registrationno: Optional[str] = Field(default=None, nullable=True)


class Farmer(VersionedModel, table=True):
    __tablename__ = "farmer" # type: ignore
    farmerid: Optional[int] = Field(default=None, primary_key=True)
    tempclientid: Optional[UUID] = Field(default=None, nullable=True)
    firstname: Optional[str] = Field(default=None, nullable=True)
    middlename: Optional[str] = Field(default=None, nullable=True)
    lastname: Optional[str] = Field(default=None, nullable=True)
    gender: Optional[str] = Field(default=None, nullable=True)
    dateofbirth: Optional[date] = Field(default=None, nullable=True)
    email: Optional[str] = Field(default=None, nullable=True)
    phonenumber: Optional[str] = Field(default=None, nullable=True)
    associationid: Optional[int] = Field(default=None, foreign_key="association.associationid")
    householdsize: Optional[int] = Field(default=None, nullable=True)
    availablelabor: Optional[int] = Field(default=None, nullable=True)
    photourl: Optional[str] = Field(default=None, nullable=True)
    userid: Optional[int] = Field(default=None, nullable=True)


class Farmtype(TimestampModel, table=True):
    __tablename__ = "farmtype" # type: ignore
    farmtypeid: Optional[int] = Field(default=None, primary_key=True)
    typename: Optional[str] = Field(default=None, nullable=True)


class Farm(VersionedModel, table=True):
    __tablename__ = "farm" # type: ignore
    farmid: Optional[int] = Field(default=None, primary_key=True)
    tempclientid: Optional[UUID] = Field(default=None, nullable=True)
    farmerid: Optional[int] = Field(default=None, foreign_key="farmer.farmerid")
    farmtypeid: Optional[int] = Field(default=None, foreign_key="farmtype.farmtypeid")
    farmsize: Optional[Decimal] = Field(default=None, nullable=True)


# DATA COLLECTION MODELS
class Season(VersionedModel, table=True):
    __tablename__ = "season" # type: ignore
    seasonid: Optional[int] = Field(default=None, primary_key=True)
    tempclientid: Optional[UUID] = Field(default=None, nullable=True)
    name: Optional[str] = Field(default=None, nullable=True)
    year: Optional[int] = Field(default=None, nullable=True)
    startdate: Optional[date] = Field(default=None, nullable=True)
    enddate: Optional[date] = Field(default=None, nullable=True)


class Crop(TimestampModel, table=True):
    __tablename__ = "crop" # type: ignore
    croptypeid: Optional[int] = Field(default=None, primary_key=True)
    name: Optional[str] = Field(default=None, nullable=True)


class CropRegistry(VersionedModel, table=True):
    __tablename__ = "cropregistry" # type: ignore
    cropregistryid: Optional[int] = Field(default=None, primary_key=True)
    tempclientid: Optional[UUID] = Field(default=None, nullable=True)
    farmid: Optional[int] = Field(default=None, foreign_key="farm.farmid")
    seasonid: Optional[int] = Field(default=None, foreign_key="season.seasonid")
    croptypeid: Optional[int] = Field(default=None, foreign_key="crop.croptypeid")
    cropvariety: Optional[str] = Field(default=None, nullable=True)
    areaplanted: Optional[Decimal] = Field(default=None, nullable=True)
    plantedquantity: Optional[Decimal] = Field(default=None, nullable=True)
    plantingdate: Optional[date] = Field(default=None, nullable=True)
    harvestdate: Optional[date] = Field(default=None, nullable=True)
    areaharvested: Optional[Decimal] = Field(default=None, nullable=True)
    yieldquantity: Optional[Decimal] = Field(default=None, nullable=True)


class Livestock(TimestampModel, table=True):
    __tablename__ = "livestock" # type: ignore
    livestocktypeid: Optional[int] = Field(default=None, primary_key=True)
    name: Optional[str] = Field(default=None, nullable=True)


class LivestockRegistry(VersionedModel, table=True):
    __tablename__ = "livestockregistry" # type: ignore
    livestockregistryid: Optional[int] = Field(default=None, primary_key=True)
    tempclientid: Optional[UUID] = Field(default=None, nullable=True)
    farmid: Optional[int] = Field(default=None, foreign_key="farm.farmid")
    seasonid: Optional[int] = Field(default=None, foreign_key="season.seasonid")
    livestocktypeid: Optional[int] = Field(default=None, foreign_key="livestock.livestocktypeid")
    quantity: Optional[int] = Field(default=None, nullable=True)
    startdate: Optional[date] = Field(default=None, nullable=True)
    enddate: Optional[date] = Field(default=None, nullable=True)


class BusinessType(TimestampModel, table=True):
    __tablename__ = "BusinessType" # type: ignore
    businesstypeid: Optional[int] = Field(default=None, primary_key=True)
    name: Optional[str] = Field(default=None, nullable=True)


class PrimaryProduct(TimestampModel, table=True):
    __tablename__ = "PrimaryProduct" # type: ignore
    primaryproducttypeid: Optional[int] = Field(default=None, primary_key=True)
    name: Optional[str] = Field(default=None, nullable=True)


class AgroAlliedRegistry(TimestampModel, table=True):
    __tablename__ = "AgroAlliedRegistry" # type: ignore
    agroalliedregistryid: Optional[int] = Field(default=None, primary_key=True)
    farmid: Optional[int] = Field(default=None, foreign_key="farm.farmid")
    businesstypeid: Optional[int] = Field(default=None, foreign_key="BusinessType.businesstypeid")
    primaryproducttypeid: Optional[int] = Field(default=None, foreign_key="PrimaryProduct.primaryproducttypeid")
    seasonid: Optional[int] = Field(default=None, foreign_key="season.seasonid")
    tempclientid: Optional[str] = Field(default=None, nullable=True)
    productioncapacity: Optional[Decimal] = Field(default=None, nullable=True)


# NOTIFICATION MODELS
class Notification(VersionedModel, table=True):
    __tablename__ = "notification" # type: ignore
    notificationid: Optional[int] = Field(default=None, primary_key=True)
    tempclientid: Optional[UUID] = Field(default=None, nullable=True)
    createdby: Optional[int] = Field(default=None, foreign_key="useraccount.userid")
    title: Optional[str] = Field(default=None, nullable=True)
    message: Optional[str] = Field(default=None, nullable=True)
    isread: Optional[bool] = Field(default=None, nullable=True)


class Notificationtarget(TimestampModel, table=True):
    __tablename__ = "notificationtarget" # type: ignore
    targetid: Optional[int] = Field(default=None, primary_key=True)
    notificationid: Optional[int] = Field(default=None, foreign_key="notification.notificationid")
    regionid: Optional[int] = Field(default=None, foreign_key="region.regionid")
    lgaid: Optional[int] = Field(default=None, foreign_key="lga.lgaid")
    userid: Optional[int] = Field(default=None, foreign_key="useraccount.userid")


# PERMISSION MODELS
class Profileactivityparent(TimestampModel, table=True):
    __tablename__ = "profileactivityparent" # type: ignore
    activityparentid: Optional[int] = Field(default=None, primary_key=True)
    activityparentname: Optional[str] = Field(default=None, nullable=True)


class Profileactivity(TimestampModel, table=True):
    __tablename__ = "profileactivity" # type: ignore
    activityid: Optional[int] = Field(default=None, primary_key=True)
    activityparentid: Optional[int] = Field(default=None, foreign_key="profileactivityparent.activityparentid")
    activityname: Optional[str] = Field(default=None, nullable=True)


class Profileadditionalactivity(TimestampModel, table=True):
    __tablename__ = "profileadditionalactivity" # type: ignore
    additionalactivityid: Optional[int] = Field(default=None, primary_key=True)
    userid: Optional[int] = Field(default=None, foreign_key="useraccount.userid")
    activityid: Optional[int] = Field(default=None, foreign_key="profileactivity.activityid")
    canadd: Optional[bool] = Field(default=None, nullable=True)
    canedit: Optional[bool] = Field(default=None, nullable=True)
    canview: Optional[bool] = Field(default=None, nullable=True)
    candelete: Optional[bool] = Field(default=None, nullable=True)
    canapprove: Optional[bool] = Field(default=None, nullable=True)
    expireon: Optional[datetime] = Field(default=None, nullable=True)


class Dashboardmetrics(TimestampModel, table=True):
    __tablename__ = "dashboardmetrics" # type: ignore
    metric_id: Optional[int] = Field(default=None, primary_key=True)
    metric_name: Optional[int] = Field(default=None, nullable=True)
    metric_value: Optional[int] = Field(default=None, nullable=True)
    metric_createdate: Optional[datetime] = Field(default=None, nullable=True)
    metric_updateddate: Optional[datetime] = Field(default=None, nullable=True)
    sysnumber: Optional[int] = Field(default=None, nullable=True)
    createdbyuserid: Optional[int] = Field(default=None, foreign_key="useraccount.userid")
    relatedfarmerid: Optional[int] = Field(default=None, foreign_key="farmer.farmerid")
    relatedfarmid: Optional[int] = Field(default=None, foreign_key="farm.farmid")
    entityid: Optional[int] = Field(default=None, nullable=True)


class Role(SQLModel, table=True):
    __tablename__ = "role" # type: ignore
    roleid: Optional[int] = Field(default=None, primary_key=True)
    rolename: Optional[str] = Field(default=None, nullable=True)


class Synclog(SQLModel, table=True):
    __tablename__ = "synclog" # type: ignore
    synclogid: Optional[int] = Field(default=None, primary_key=True)
    tablename: Optional[str] = Field(default=None, nullable=True)
    tempclientid: Optional[UUID] = Field(default=None, nullable=True)
    serverid: Optional[int] = Field(default=None, nullable=True)
    operationtype: Optional[str] = Field(default=None, nullable=True)
    changedat: Optional[datetime] = Field(default=None, nullable=True)
    clientid: Optional[str] = Field(default=None, nullable=True)
    processed: Optional[bool] = Field(default=None, nullable=True)