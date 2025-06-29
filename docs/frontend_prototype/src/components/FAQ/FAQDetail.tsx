import React from 'react';
import { ArrowLeft, Edit, Trash2, AlertCircle, Calendar, Tag, Users } from 'lucide-react';
import { FAQ } from '../../types';
import { mockCategories } from '../../data/mockData';

interface FAQDetailProps {
  faq: FAQ;
  onBack: () => void;
  onEdit?: (faq: FAQ) => void;
  onDelete?: (faq: FAQ) => void;
  canEdit?: boolean;
}

export const FAQDetail: React.FC<FAQDetailProps> = ({
  faq,
  onBack,
  onEdit,
  onDelete,
  canEdit = false,
}) => {
  const getCategoryColor = (categoryName: string) => {
    const category = mockCategories.find(c => c.name === categoryName);
    return category?.color || 'bg-gray-100 text-gray-800';
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('ja-JP');
  };

  return (
    <div className="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <button
            onClick={onBack}
            className="flex items-center text-gray-600 hover:text-gray-900 transition-colors"
          >
            <ArrowLeft className="mr-2" size={20} />
            戻る
          </button>
          <div className="flex items-center space-x-2">
            {faq.isImportant && (
              <div className="flex items-center bg-red-100 text-red-800 px-3 py-1 rounded-full text-sm font-medium">
                <AlertCircle className="mr-1" size={16} />
                重要
              </div>
            )}
            {canEdit && (
              <>
                <button
                  onClick={() => onEdit?.(faq)}
                  className="flex items-center bg-blue-100 text-blue-700 px-4 py-2 rounded-lg hover:bg-blue-200 transition-colors"
                >
                  <Edit className="mr-2" size={16} />
                  編集
                </button>
                <button
                  onClick={() => onDelete?.(faq)}
                  className="flex items-center bg-red-100 text-red-700 px-4 py-2 rounded-lg hover:bg-red-200 transition-colors"
                >
                  <Trash2 className="mr-2" size={16} />
                  削除
                </button>
              </>
            )}
          </div>
        </div>
      </div>

      <div className="p-6">
        <div className="mb-6">
          <div className="flex items-center space-x-3 mb-4">
            <span className="text-sm font-mono text-gray-600 bg-gray-100 px-3 py-1 rounded">
              {faq.articleNumber}
            </span>
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${getCategoryColor(faq.category)}`}>
              {faq.category}
            </span>
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-4">{faq.title}</h1>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div className="flex items-center text-gray-600">
              <Users className="mr-2" size={16} />
              承認グループ: {faq.approvalGroup}
            </div>
            <div className="flex items-center text-gray-600">
              <Tag className="mr-2" size={16} />
              キーワード: {faq.keywords.join(', ')}
            </div>
            <div className="flex items-center text-gray-600">
              <Calendar className="mr-2" size={16} />
              公開期間: {formatDate(faq.publicStartDate)} ～ {formatDate(faq.publicEndDate)}
            </div>
          </div>
        </div>

        <div className="space-y-6">
          <div>
            <h2 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
              【質問】
            </h2>
            <div className="bg-blue-50 border-l-4 border-blue-400 p-4 rounded-r-lg">
              <p className="text-gray-800 leading-relaxed whitespace-pre-wrap">
                {faq.question}
              </p>
            </div>
          </div>

          <div>
            <h2 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
              【回答】
            </h2>
            <div className="bg-green-50 border-l-4 border-green-400 p-4 rounded-r-lg">
              <p className="text-gray-800 leading-relaxed whitespace-pre-wrap">
                {faq.answer}
              </p>
            </div>
          </div>

          {faq.additionalComment && (
            <div>
              <h2 className="text-lg font-semibold text-gray-900 mb-3">
                【追加コメント】
              </h2>
              <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded-r-lg">
                <p className="text-gray-800 leading-relaxed whitespace-pre-wrap">
                  {faq.additionalComment}
                </p>
              </div>
            </div>
          )}

          {faq.notes && (
            <div>
              <h2 className="text-lg font-semibold text-gray-900 mb-3">
                【備考】
              </h2>
              <div className="bg-gray-50 border-l-4 border-gray-400 p-4 rounded-r-lg">
                <p className="text-gray-800 leading-relaxed whitespace-pre-wrap">
                  {faq.notes}
                </p>
              </div>
            </div>
          )}
        </div>

        <div className="mt-8 pt-6 border-t border-gray-200">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-600">
            <div>
              <strong>投稿者:</strong> {faq.authorName}
            </div>
            <div>
              <strong>投稿日:</strong> {formatDate(faq.createdAt)}
            </div>
            {faq.approvedAt && (
              <>
                <div>
                  <strong>承認日:</strong> {formatDate(faq.approvedAt)}
                </div>
                <div>
                  <strong>承認者:</strong> {faq.approvedBy || '未設定'}
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};