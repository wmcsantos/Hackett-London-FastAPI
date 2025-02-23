from typing import List, Optional

from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKeyConstraint, Index, Numeric, PrimaryKeyConstraint, SmallInteger, String, Table, Text, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
import datetime
import decimal

class Base(DeclarativeBase):
    pass


class Categories(Base):
    __tablename__ = 'categories'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='idx_16402_primary'),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(45))
    parent_id: Mapped[int] = mapped_column(BigInteger)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))

    product: Mapped[List['Products']] = relationship('Products', secondary='category_products', back_populates='category')


class Colors(Base):
    __tablename__ = 'colors'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='idx_16411_primary'),
        Index('idx_16411_name', 'name', unique=True),
        Index('idx_16411_name_2', 'name', unique=True)
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    code: Mapped[str] = mapped_column(String(5))
    image_url: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))

    color_products: Mapped[List['ColorProducts']] = relationship('ColorProducts', back_populates='color')


class PasswordResets(Base):
    __tablename__ = 'password_resets'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='idx_16433_primary'),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger)
    token: Mapped[str] = mapped_column(String(255))
    createdat: Mapped[datetime.datetime] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))
    expiration: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))


class Products(Base):
    __tablename__ = 'products'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='idx_16439_primary'),
        Index('idx_16439_reference1', 'reference1', unique=True)
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))
    reference1: Mapped[str] = mapped_column(String(15))
    description_details: Mapped[Optional[str]] = mapped_column(Text)
    description_composition: Mapped[Optional[str]] = mapped_column(Text)
    description_care: Mapped[Optional[str]] = mapped_column(Text)
    description_delivery: Mapped[Optional[str]] = mapped_column(Text)
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))

    category: Mapped[List['Categories']] = relationship('Categories', secondary='category_products', back_populates='product')
    color_products: Mapped[List['ColorProducts']] = relationship('ColorProducts', back_populates='product')
    product_variants: Mapped[List['ProductVariants']] = relationship('ProductVariants', back_populates='product')


class Sizes(Base):
    __tablename__ = 'sizes'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='idx_16459_primary'),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(10))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))

    product_variants: Mapped[List['ProductVariants']] = relationship('ProductVariants', back_populates='size')


class Users(Base):
    __tablename__ = 'users'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='idx_16465_primary'),
        Index('idx_16465_email', 'email', unique=True)
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    title: Mapped[str] = mapped_column(String(50))
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    gender: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(252))
    password_hash: Mapped[str] = mapped_column(String(1000))
    is_admin: Mapped[bool] = mapped_column(Boolean)
    remember_token: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))
    email_verified_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))

    carts: Mapped[List['Carts']] = relationship('Carts', back_populates='user')
    orders: Mapped[List['Orders']] = relationship('Orders', back_populates='user')


class Carts(Base):
    __tablename__ = 'carts'
    __table_args__ = (
        ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='RESTRICT', onupdate='RESTRICT', name='carts_ibfk_1'),
        PrimaryKeyConstraint('id', name='idx_16389_primary'),
        Index('idx_16389_user_id', 'user_id')
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger)
    cart_status: Mapped[str] = mapped_column(String(30), server_default=text("'active'::character varying"))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))
    session_id: Mapped[Optional[str]] = mapped_column(String(100))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))

    user: Mapped['Users'] = relationship('Users', back_populates='carts')
    cart_items: Mapped[List['CartItems']] = relationship('CartItems', back_populates='cart')


t_category_products = Table(
    'category_products', Base.metadata,
    Column('product_id', BigInteger, nullable=False),
    Column('category_id', BigInteger, nullable=False),
    ForeignKeyConstraint(['category_id'], ['categories.id'], ondelete='CASCADE', onupdate='CASCADE', name='category_products_ibfk_2'),
    ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE', onupdate='CASCADE', name='category_products_ibfk_1'),
    Index('idx_16407_category_products_ibfk_1', 'product_id'),
    Index('idx_16407_category_products_ibfk_2', 'category_id')
)


class ColorProducts(Base):
    __tablename__ = 'color_products'
    __table_args__ = (
        ForeignKeyConstraint(['color_id'], ['colors.id'], ondelete='RESTRICT', onupdate='RESTRICT', name='color_products_ibfk_1'),
        ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE', onupdate='RESTRICT', name='color_products_ibfk_2'),
        PrimaryKeyConstraint('id', name='idx_16417_primary'),
        Index('idx_16417_color_id', 'color_id'),
        Index('idx_16417_color_products_ibfk_2', 'product_id')
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    product_id: Mapped[int] = mapped_column(BigInteger)
    color_id: Mapped[int] = mapped_column(BigInteger)

    color: Mapped['Colors'] = relationship('Colors', back_populates='color_products')
    product: Mapped['Products'] = relationship('Products', back_populates='color_products')
    product_images: Mapped[List['ProductImages']] = relationship('ProductImages', back_populates='color_products')
    product_variants: Mapped[List['ProductVariants']] = relationship('ProductVariants', back_populates='color_products')


class Orders(Base):
    __tablename__ = 'orders'
    __table_args__ = (
        ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='RESTRICT', onupdate='RESTRICT', name='orders_ibfk_1'),
        PrimaryKeyConstraint('id', name='idx_16422_primary'),
        Index('idx_16422_user_id', 'user_id')
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger)
    order_status: Mapped[str] = mapped_column(String(50))
    order_date: Mapped[datetime.datetime] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))
    total_amount: Mapped[decimal.Decimal] = mapped_column(Numeric(10, 2))
    shipping_address: Mapped[str] = mapped_column(String(255))

    user: Mapped['Users'] = relationship('Users', back_populates='orders')
    order_items: Mapped[List['OrderItems']] = relationship('OrderItems', back_populates='order')


class ProductImages(Base):
    __tablename__ = 'product_images'
    __table_args__ = (
        ForeignKeyConstraint(['color_products_id'], ['color_products.id'], ondelete='CASCADE', onupdate='RESTRICT', name='product_images_ibfk_1'),
        PrimaryKeyConstraint('id', name='idx_16447_primary'),
        Index('idx_16447_product_images_ibfk_1', 'color_products_id')
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    color_products_id: Mapped[int] = mapped_column(BigInteger)
    image_url: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))
    position: Mapped[Optional[int]] = mapped_column(SmallInteger)
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))

    color_products: Mapped['ColorProducts'] = relationship('ColorProducts', back_populates='product_images')


class ProductVariants(Base):
    __tablename__ = 'product_variants'
    __table_args__ = (
        ForeignKeyConstraint(['color_products_id'], ['color_products.id'], ondelete='CASCADE', onupdate='RESTRICT', name='product_variants_ibfk_3'),
        ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE', onupdate='RESTRICT', name='product_variants_ibfk_1'),
        ForeignKeyConstraint(['size_id'], ['sizes.id'], ondelete='CASCADE', onupdate='RESTRICT', name='product_variants_ibfk_2'),
        PrimaryKeyConstraint('id', name='idx_16453_primary'),
        Index('idx_16453_color_products_id', 'color_products_id'),
        Index('idx_16453_product_id', 'product_id'),
        Index('idx_16453_size_id', 'size_id')
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    stock: Mapped[int] = mapped_column(BigInteger)
    product_id: Mapped[int] = mapped_column(BigInteger)
    size_id: Mapped[int] = mapped_column(BigInteger)
    price: Mapped[decimal.Decimal] = mapped_column(Numeric(10, 2))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))
    color_products_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    reference2: Mapped[Optional[str]] = mapped_column(String(10))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))

    color_products: Mapped['ColorProducts'] = relationship('ColorProducts', back_populates='product_variants')
    product: Mapped['Products'] = relationship('Products', back_populates='product_variants')
    size: Mapped['Sizes'] = relationship('Sizes', back_populates='product_variants')
    cart_items: Mapped[List['CartItems']] = relationship('CartItems', back_populates='product_variant')
    order_items: Mapped[List['OrderItems']] = relationship('OrderItems', back_populates='product_variant')


class CartItems(Base):
    __tablename__ = 'cart_items'
    __table_args__ = (
        ForeignKeyConstraint(['cart_id'], ['carts.id'], ondelete='RESTRICT', onupdate='RESTRICT', name='cart_items_ibfk_1'),
        ForeignKeyConstraint(['product_variant_id'], ['product_variants.id'], ondelete='CASCADE', onupdate='RESTRICT', name='cart_items_ibfk_2'),
        PrimaryKeyConstraint('id', name='idx_16396_primary'),
        Index('idx_16396_cart_id', 'cart_id'),
        Index('idx_16396_cart_items_ibfk_2', 'product_variant_id')
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    cart_id: Mapped[int] = mapped_column(BigInteger)
    product_variant_id: Mapped[int] = mapped_column(BigInteger)
    quantity: Mapped[int] = mapped_column(BigInteger)
    price: Mapped[decimal.Decimal] = mapped_column(Numeric(5, 2))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))

    cart: Mapped['Carts'] = relationship('Carts', back_populates='cart_items')
    product_variant: Mapped['ProductVariants'] = relationship('ProductVariants', back_populates='cart_items')


class OrderItems(Base):
    __tablename__ = 'order_items'
    __table_args__ = (
        ForeignKeyConstraint(['order_id'], ['orders.id'], ondelete='RESTRICT', onupdate='RESTRICT', name='order_items_ibfk_1'),
        ForeignKeyConstraint(['product_variant_id'], ['product_variants.id'], ondelete='CASCADE', onupdate='RESTRICT', name='order_items_ibfk_2'),
        PrimaryKeyConstraint('id', name='idx_16428_primary'),
        Index('idx_16428_order_id', 'order_id'),
        Index('idx_16428_order_items_ibfk_2', 'product_variant_id')
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    order_id: Mapped[int] = mapped_column(BigInteger)
    product_variant_id: Mapped[int] = mapped_column(BigInteger)
    quantity: Mapped[int] = mapped_column(BigInteger)
    price: Mapped[decimal.Decimal] = mapped_column(Numeric(5, 2))

    order: Mapped['Orders'] = relationship('Orders', back_populates='order_items')
    product_variant: Mapped['ProductVariants'] = relationship('ProductVariants', back_populates='order_items')
