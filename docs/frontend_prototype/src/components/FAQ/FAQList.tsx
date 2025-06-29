import React from 'react';
import { AlertCircle, Eye, Edit, Trash2, Clock, CheckCircle } from 'lucide-react';
import { FAQ } from '../../types';
import { mockCategories } from '../../data/mockData';

interface FAQListProps {
  faqs: FAQ[];
  onFAQClick: (faq: FAQ) => void;
  showActions?: boolean;
  onEdit?: (faq: FAQ) => void;
  onDelete?: (faq: FAQ) => void;
}

export const FAQList: React.FC<FAQListProps> = ({
  faqs,
  onFAQClick,
  showActions = false,
  onEdit,
  onDelete,
}) => {
  const getCategoryColor = (categoryName: string) => {
    const category = mockCategories.find(c => c.name === categoryName);
    return category?.color || 'bg-gray-100 text-gray-800';
  };

  const getStatusBadge = (status: FAQ['status']) => {
    switch (status) {
      case 'approved':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
            <CheckCircle className="mr-1" size={12} />
            承認済み
          </span>
        );
      case 'pending':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
            <Clock className="mr-1" size={12} />
            承認待ち
          </span>
        );
      case 'rejected':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
            却下
          </span>
        );
      case 'draft':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
            下書き
          </span>
        );
      default:
        return null;
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('ja-JP');
  };

  if (faqs.length === 0) {
    return (
      <div className="text-center py-12 bg-white rounded-xl shadow-lg border border-gray-200">
        <div className="text-gray-400 mb-4">
          <Eye size={48} className="mx-auto" />
        </div>
        <p className="text-gray-500 text-lg">該当するFAQが見つかりませんでした</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900">
            検索結果: {faqs.length}件
          </h3>
        </div>
      </div>

      <div className="divide-y divide-gray-100">
        {faqs.map((faq) => (
          <div
            key={faq.id}
            className="p-6 hover:bg-gray-50 transition-colors cursor-pointer"
            onClick={() => onFAQClick(faq)}
          >
            <div className="flex items-start justify-between">
              <div className="flex-1 min-w-0">
                <div className="flex items-center space-x-3 mb-2">
                  {faq.isImportant && (
                    <AlertCircle className="text-red-500 flex-shrink-0" size={20} />
                  )}
                  <span className="text-sm font-mono text-gray-600 bg-gray-100 px-2 py-1 rounded">
                    {faq.articleNumber}
                  </span>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getCategoryColor(faq.category)}`}>
                    {faq.category}
                  </span>
                  <span className="px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                    {faq.approvalGroup}
                  </span>
                  {getStatusBadge(faq.status)}
                </div>

                <h4 className="text-lg font-semibold text-gray-900 mb-2 line-clamp-1">
                  {faq.title}
                </h4>

                <p className="text-gray-600 mb-3 line-clamp-2">
                  【質問】{faq.question}
                </p>

                <div className="flex flex-wrap items-center text-sm text-gray-500 space-x-4">
                  <span>投稿日: {formatDate(faq.createdAt)}</span>
                  {faq.approvedAt && (
                    <span>承認日: {formatDate(faq.approvedAt)}</span>
                  )}
                  <span>
                    キーワード: {faq.keywords.join(', ')}
                  </span>
                </div>
              </div>

              {showActions && (
                <div className="flex items-center space-x-2 ml-4">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onEdit?.(faq);
                    }}
                    className="p-2 text-blue-600 hover:bg-blue-100 rounded-md transition-colors"
                  >
                    <Edit size={16} />
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onDelete?.(faq);
                    }}
                    className="p-2 text-red-600 hover:bg-red-100 rounded-md transition-colors"
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};